"""AI Router - Chatbot, Recommendations, Image Generation"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional, List

from backend.database import get_db
from backend.models.ai_engine import AISession, AIMessage, ProductRecommendation, AIGeneratedImage, SearchQuery
from backend.models.product import Product
from backend.schemas.product import ProductResponse
from backend.core.auth import get_current_user, get_current_user_required
from backend.core.config import is_module_active

router = APIRouter(prefix="/api/ai", tags=["AI"])


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[int] = None


class ChatResponse(BaseModel):
    session_id: int
    reply: str
    recommendations: List[ProductResponse] = []


class ImageGenRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    style: Optional[str] = "realistic"
    size: Optional[str] = "1024x1024"


@router.post("/chat", response_model=ChatResponse)
async def ai_chat(data: ChatMessage, db: Session = Depends(get_db), user: Optional[dict] = Depends(get_current_user)):
    if not is_module_active("ai_engine"):
        raise HTTPException(status_code=403, detail="AI module not active on this platform")

    # Get or create session
    if data.session_id:
        session = db.get(AISession, data.session_id)
        if not session:
            session = AISession(user_id=user["id"] if user else None)
            db.add(session)
    else:
        session = AISession(user_id=user["id"] if user else None)
        db.add(session)
        db.flush()

    # Save user message
    user_msg = AIMessage(session_id=session.id, role="user", content=data.message)
    db.add(user_msg)

    # Simple AI response (placeholder - integrate with LangChain/OpenAI in production)
    reply = generate_ai_response(data.message, db)

    # Save assistant response
    assistant_msg = AIMessage(session_id=session.id, role="assistant", content=reply)
    db.add(assistant_msg)

    db.commit()
    db.refresh(session)

    # Get recommendations
    recs = db.execute(
        select(Product).where(Product.status == "active").limit(5)
    ).scalars().all()

    return ChatResponse(
        session_id=session.id,
        reply=reply,
        recommendations=[ProductResponse.model_validate(r) for r in recs],
    )


def generate_ai_response(message: str, db: Session) -> str:
    """Simple AI response - replace with LangChain/OpenAI in production"""
    msg_lower = message.lower()

    if any(k in msg_lower for k in ["hello", "hi", "chào", "xin chào"]):
        return "Xin chào! Tôi có thể giúp gì cho bạn hôm nay? Tôi có thể gợi ý sản phẩm, trả lời câu hỏi về đơn hàng, hoặc tư vấn mua hàng."
    elif any(k in msg_lower for k in ["recommend", "gợi ý", "suggest", "tôi nên"]):
        return "Dựa trên sở thích của bạn, tôi gợi ý một số sản phẩm bán chạy. Hãy xem các sản phẩm được hiển thị bên dưới nhé!"
    elif any(k in msg_lower for k in ["order", "đơn hàng", "tracking", "vận chuyển"]):
        return "Bạn có thể theo dõi đơn hàng trong mục 'Đơn hàng' của tài khoản. Nếu cần hỗ trợ thêm, vui lòng cung cấp mã đơn hàng."
    elif any(k in msg_lower for k in ["return", "đổi trả", "refund", "hoàn tiền"]):
        return "Chính sách đổi trả của chúng tôi: Đổi trả trong 7 ngày với sản phẩm còn nguyên seal. Liên hệ hotline hoặc email để được hỗ trợ."
    elif any(k in msg_lower for k in ["payment", "thanh toán", "pay"]):
        return "Chúng tôi hỗ trợ nhiều phương thức thanh toán: COD (nhận hàng rồi trả tiền), thẻ Visa/Mastercard, chuyển khoản ngân hàng, MoMo, VNPay."
    else:
        return f"Cảm ơn bạn đã nhắn tin! Tôi đã ghi nhận: '{message}'. Hiện tại tôi đang ở chế độ demo - trong phiên bản đầy đủ, tôi sẽ sử dụng AI nâng cao để trả lời chính xác hơn."


@router.get("/recommendations", response_model=List[ProductResponse])
async def get_recommendations(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db), user: Optional[dict] = Depends(get_current_user)):
    if not is_module_active("ai_engine"):
        raise HTTPException(status_code=403, detail="AI module not active")

    # Get trending + featured products as "recommendations"
    products = db.execute(
        select(Product).where(
            Product.status == "active"
        ).order_by(
            func.random()
        ).limit(limit)
    ).scalars().all()
    return [ProductResponse.model_validate(p) for p in products]


@router.post("/image/generate")
async def generate_image(data: ImageGenRequest, db: Session = Depends(get_db), user: dict = Depends(get_current_user_required)):
    if not is_module_active("ai_engine"):
        raise HTTPException(status_code=403, detail="AI module not active")

    # Create pending generation record
    gen = AIGeneratedImage(
        user_id=user["id"],
        prompt=data.prompt,
        negative_prompt=data.negative_prompt,
        style=data.style,
        size=data.size,
        status="pending",
    )
    db.add(gen)
    db.commit()
    db.refresh(gen)

    # In production: call Stable Diffusion / DALL-E / local model
    # For now, return mock result
    return {
        "id": gen.id,
        "status": "completed",
        "image_url": None,
        "message": "Image generation queued. In production, this would call a real AI model (Stable Diffusion, DALL-E, or local model like SDXL on RTX 5080).",
        "prompt": data.prompt,
    }


@router.get("/sessions")
async def get_ai_sessions(db: Session = Depends(get_db), user: dict = Depends(get_current_user_required)):
    sessions = db.execute(
        select(AISession).where(AISession.user_id == user["id"]).order_by(AISession.updated_at.desc()).limit(20)
    ).scalars().all()
    return [{"id": s.id, "session_type": s.session_type, "created_at": s.created_at.isoformat(), "updated_at": s.updated_at.isoformat()} for s in sessions]
