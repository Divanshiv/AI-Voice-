from fastapi import APIRouter, HTTPException
from app.models.chat_models import ChatRequest, ChatResponse, Message
from app.services.ai_service import ai_service
from app.services.conversation import conversation_service


router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    user_message = request.message.strip()
    language = request.language or "en"
    
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    exit_msg_en = "Thank you for chatting with me! Have a great day!"
    exit_msg_hi = "मेरे साथ चैट करने के लिए धन्यवाद! आपका दिन शुभ हो!"
    
    goodbye_en = ["exit", "goodbye", "bye", "quit"]
    goodbye_hi = ["exit", "goodbye", "bye", "quit", "बाहर", "अलविदा"]
    
    if user_message.lower() in goodbye_en or user_message in goodbye_hi:
        conversation_service.add_message(request.session_id, "user", user_message)
        response_text = exit_msg_hi if language == "hi" else exit_msg_en
        conversation_service.add_message(request.session_id, "assistant", response_text)
        ai_service.clear_session(request.session_id)
        conversation_service.clear_session(request.session_id)
        return ChatResponse(
            response=response_text,
            options=[],
            session_id=request.session_id
        )
    
    if user_message.lower() in ["repeat", "please repeat that", "say that again", "दोहराओ", "फिर से बोल"]:
        last_response = conversation_service.get_last_response(request.session_id)
        if last_response:
            return ChatResponse(
                response=last_response,
                options=ai_service.get_menu_options(),
                session_id=request.session_id
            )
        return ChatResponse(
            response="There's nothing to repeat yet. Let's start a conversation!" if language == "en" else "दोहराने के लिए कुछ नहीं है। चलो बातचीत शुरू करते हैं!",
            options=ai_service.get_menu_options(),
            session_id=request.session_id
        )
    
    if user_message.lower() in ["learn about our product", "learn about your product", "tell me about your product", "product info", "उत्पाद", "product"]:
        product_text = ai_service.get_product_info_text(language)
        conversation_service.add_message(request.session_id, "user", user_message)
        conversation_service.add_message(request.session_id, "assistant", product_text)
        return ChatResponse(
            response=product_text,
            options=ai_service.get_menu_options(),
            session_id=request.session_id
        )
    
    conversation_service.add_message(request.session_id, "user", user_message)
    
    response_text, options = ai_service.generate_response(user_message, request.session_id, language)
    
    conversation_service.add_message(request.session_id, "assistant", response_text)
    
    return ChatResponse(
        response=response_text,
        options=options,
        session_id=request.session_id
    )


@router.get("/history/{session_id}")
async def get_history(session_id: str):
    messages = conversation_service.get_history(session_id)
    return {
        "session_id": session_id,
        "messages": [
            {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp}
            for msg in messages
        ]
    }