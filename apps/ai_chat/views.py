import json
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from .models import AISettings, ChatHistory
from .tools import (
    TOOLS_REGISTRY, openai_tools_format,
    anthropic_tools_format, get_handler,
)

logger = logging.getLogger(__name__)
HISTORY_LIMIT = 10


def build_context_text(context_data):
    """Frontend yuborgan foydalanuvchi ma'lumotlarini matn ko'rinishiga o'tkazish."""
    parts = []
    tasks = context_data.get('tasks', [])
    if tasks:
        today_tasks = [t for t in tasks if not t.get('done')]
        done_tasks = [t for t in tasks if t.get('done')]
        parts.append("Foydalanuvchi joriy ma'lumotlari:")
        parts.append(
            f"- Bajarilmagan vazifalar ({len(today_tasks)} ta): "
            + ', '.join(t.get('title', '') for t in today_tasks[:5])
        )
        parts.append(f"- Bajarilgan vazifalar: {len(done_tasks)} ta")
    focus_sessions = context_data.get('focusSessions', [])
    if focus_sessions:
        total_mins = sum(s.get('mins', 0) for s in focus_sessions[-10:])
        parts.append(f"- So'nggi focus vaqti: {total_mins} daqiqa")
    streak = context_data.get('streak', 0)
    if streak:
        parts.append(f"- Streak: {streak} kun ketma-ket")
    transactions = context_data.get('transactions', [])
    if transactions:
        income = sum(t.get('amt', 0) for t in transactions if t.get('type') == 'income')
        expense = sum(t.get('amt', 0) for t in transactions if t.get('type') == 'expense')
        parts.append(f"- Daromad: {income:,} so'm, Harajat: {expense:,} so'm")
    stats = context_data.get('stats', {})
    if stats:
        parts.append(f"- Bugun: {stats.get('todayDone', 0)}/{stats.get('todayTotal', 0)} vazifa bajarildi")
        parts.append(f"- Bu hafta focus: {stats.get('weekFocusMins', 0)} daqiqa")
    return '\n'.join(parts) if parts else ''


@method_decorator(
    ratelimit(key='user', rate='30/m', method='POST', block=True),
    name='dispatch'
)
class AIChatView(APIView):
    permission_classes = [IsAuthenticated]

    def _history_messages(self, user):
        """Foydalanuvchining oxirgi N ta xabar juftligini AI formatida qaytaradi."""
        recent = ChatHistory.objects.filter(user=user).order_by('-created_at')[:HISTORY_LIMIT * 2]
        history = list(reversed(recent))
        return [{'role': h.role, 'content': h.content} for h in history]

    # ── OpenAI (tool-loop) ──────────────────────────────────────
    def _call_openai(self, client, settings, system, messages):
        tools = openai_tools_format()
        # 1-chaqiruv
        resp = client.chat.completions.create(
            model=settings.model_name,
            messages=[{'role': 'system', 'content': system}] + messages,
            tools=tools,
            tool_choice='auto',
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
        )
        msg = resp.choices[0].message

        # Tool call yo'q — oddiy javob
        if not msg.tool_calls:
            return msg.content.strip()

        # Tool call bor — handlerlarni ishga tushir
        tool_results_msgs = [msg]  # assistant xabari (tool_calls ichida)
        for tc in msg.tool_calls:
            fn_name = tc.function.name
            fn_args = json.loads(tc.function.arguments or '{}')
            handler = get_handler(fn_name)
            if handler:
                result = handler(user=self.request.user, **fn_args)
            else:
                result = {'error': f"Tool '{fn_name}' topilmadi"}
            tool_results_msgs.append({
                'role': 'tool',
                'tool_call_id': tc.id,
                'content': json.dumps(result, ensure_ascii=False),
            })

        # 2-chaqiruv — natijalar bilan
        resp2 = client.chat.completions.create(
            model=settings.model_name,
            messages=[{'role': 'system', 'content': system}] + messages + tool_results_msgs,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
        )
        return resp2.choices[0].message.content.strip()

    # ── Anthropic (tool-loop) ───────────────────────────────────
    def _call_anthropic(self, client, settings, system, messages):
        tools = anthropic_tools_format()
        # 1-chaqiruv
        resp = client.messages.create(
            model=settings.model_name,
            max_tokens=settings.max_tokens,
            system=system,
            tools=tools,
            messages=messages,
        )

        # Tool use yo'q — oddiy javob
        if resp.stop_reason != 'tool_use':
            return resp.content[0].text.strip()

        # Tool use bor — handlerlarni ishga tushir
        tool_results = []
        for block in resp.content:
            if block.type != 'tool_use':
                continue
            handler = get_handler(block.name)
            if handler:
                result = handler(user=self.request.user, **block.input)
            else:
                result = {'error': f"Tool '{block.name}' topilmadi"}
            tool_results.append({
                'type': 'tool_result',
                'tool_use_id': block.id,
                'content': json.dumps(result, ensure_ascii=False),
            })

        # 2-chaqiruv — natijalar bilan
        messages_with_results = messages + [
            {'role': 'assistant', 'content': resp.content},
            {'role': 'user', 'content': tool_results},
        ]
        resp2 = client.messages.create(
            model=settings.model_name,
            max_tokens=settings.max_tokens,
            system=system,
            messages=messages_with_results,
        )
        return resp2.content[0].text.strip()

    # ── Gemini ──────────────────────────────────────────────────
    def _call_gemini(self, client_key, settings, system, messages):
        """Google Gemini API (tekin tier: 60 req/min)"""
        import requests

        # Gemini format: barcha xabarlarni birlashtirib yuborish
        conversation = system + "\n\n"
        for msg in messages:
            role = "Foydalanuvchi" if msg['role'] == 'user' else "AI"
            conversation += f"{role}: {msg['content']}\n"
        conversation += "AI:"

        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{settings.model_name}:generateContent",
            headers={"Content-Type": "application/json"},
            params={"key": client_key},
            json={
                "contents": [{"parts": [{"text": conversation}]}],
                "generationConfig": {
                    "maxOutputTokens": settings.max_tokens,
                    "temperature": settings.temperature,
                },
                "safetySettings": [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                ]
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            return data['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            raise Exception(f"Gemini xato: {response.status_code} — {response.text[:200]}")

    # ── Ollama ──────────────────────────────────────────────────
    def _call_ollama(self, settings, system, messages):
        """Ollama — mahalliy, butunlay bepul (llama3, qwen2.5, mistral)"""
        import requests

        ollama_messages = [{"role": "system", "content": system}] + messages

        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": settings.model_name or "llama3",
                "messages": ollama_messages,
                "stream": False,
                "options": {"temperature": settings.temperature}
            },
            timeout=60
        )

        if response.status_code == 200:
            return response.json()['message']['content'].strip()
        raise Exception(f"Ollama xato: {response.status_code}")

    # ── Asosiy endpoint ─────────────────────────────────────────
    def post(self, request):
        if getattr(request, 'limited', False):
            return Response(
                {'message': "Juda ko'p so'rov. 1 daqiqadan so'ng qayta urining."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        message = request.data.get('message', '').strip()
        context_data = request.data.get('context', {})

        if not message:
            return Response({'message': "Xabar bo'sh"}, status=status.HTTP_400_BAD_REQUEST)

        ai_settings = AISettings.objects.filter(is_active=True).first()

        # AI sozlanmagan yoki offline rejim — OfflineAIEngine ishlatish
        if not ai_settings or ai_settings.provider == 'offline':
            from .offline_engine import OfflineAIEngine
            engine = OfflineAIEngine(request.user)
            reply = engine.respond(message)
            ChatHistory.objects.create(user=request.user, role='user', content=message)
            ChatHistory.objects.create(user=request.user, role='assistant', content=reply)
            return Response({'reply': reply})

        context_text = build_context_text(context_data)
        full_system = ai_settings.system_prompt
        if context_text:
            full_system += f'\n\n{context_text}'

        # Tool qobiliyatlari haqida AI'ni xabardor qilish
        tool_names = ', '.join(t['name'] for t in TOOLS_REGISTRY)
        full_system += (
            f"\n\nSizda foydalanuvchi ma'lumotlarini real vaqtda olish va o'zgartirish uchun "
            f"quyidagi toollar mavjud: {tool_names}. "
            f"Foydalanuvchi so'raganda tegishli toolni ishlating."
        )

        history_msgs = self._history_messages(request.user)
        all_messages = history_msgs + [{'role': 'user', 'content': message}]

        reply = ''
        try:
            if ai_settings.provider == 'openai':
                import openai
                client = openai.OpenAI(api_key=ai_settings.api_key)
                reply = self._call_openai(client, ai_settings, full_system, all_messages)

            elif ai_settings.provider == 'anthropic':
                import anthropic
                client = anthropic.Anthropic(api_key=ai_settings.api_key)
                reply = self._call_anthropic(client, ai_settings, full_system, all_messages)

            elif ai_settings.provider == 'gemini':
                reply = self._call_gemini(ai_settings.api_key, ai_settings, full_system, all_messages)

            elif ai_settings.provider == 'ollama':
                reply = self._call_ollama(ai_settings, full_system, all_messages)

        except Exception as e:
            logger.error(
                f'AI chat xatosi (provider={ai_settings.provider}): {e}', exc_info=True
            )
            # Fallback — offline engine
            try:
                from .offline_engine import OfflineAIEngine
                engine = OfflineAIEngine(request.user)
                reply = engine.respond(message)
            except Exception:
                return Response(
                    {'reply': "AI hozir javob bera olmadi. Keyinroq urinib ko'ring."},
                    status=status.HTTP_200_OK,
                )

        ChatHistory.objects.create(user=request.user, role='user', content=message)
        ChatHistory.objects.create(user=request.user, role='assistant', content=reply)

        return Response({'reply': reply})
