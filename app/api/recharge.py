from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.db.mongo import get_collection
from app.api.v1.auth.login import get_current_user
from app.models.user import User

router = APIRouter(prefix="/recharge", tags=["充值模块"])

# ------------------------------
# 数据模型
# ------------------------------
class CreateOrderRequest(BaseModel):
    amount: float

class PayRequest(BaseModel):
    order_id: str

# ------------------------------
# 1. 创建充值订单
# ------------------------------
@router.post("/create_order")
async def create_order(req: CreateOrderRequest, current_user: User = Depends(get_current_user)):
    user_coll = get_collection("users")
    user = user_coll.find_one({"id": current_user.id})
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    openid = user.get("openid")
    if not openid:
        raise HTTPException(status_code=400, detail="用户OpenID缺失")

    coll = get_collection("recharge_orders")

    order = {
        "openid": openid,
        "amount": req.amount,
        "status": "pending",  # pending / paid / failed
        "create_time": datetime.now(),
        "pay_time": None
    }

    res = coll.insert_one(order)
    return {
        "code": 0,
        "msg": "订单创建成功",
        "data": {
            "order_id": str(res.inserted_id),
            "amount": req.amount
        }
    }

# ------------------------------
# 2. 模拟支付（课程项目必用，不用真微信支付）
# ------------------------------
@router.post("/pay")
async def pay(req: PayRequest, current_user: User = Depends(get_current_user)):
    user_coll = get_collection("users")
    user = user_coll.find_one({"id": current_user.id})
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    openid = user.get("openid")
    if not openid:
        raise HTTPException(status_code=400, detail="用户OpenID缺失")

    order_coll = get_collection("recharge_orders")

    # 查找订单
    order = order_coll.find_one({"_id": req.order_id})
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 验证订单属于当前用户
    if order.get("openid") != openid:
        raise HTTPException(status_code=403, detail="无权操作此订单")

    if order["status"] == "paid":
        raise HTTPException(status_code=400, detail="已支付")

    # 标记支付成功
    order_coll.update_one(
        {"_id": req.order_id},
        {"$set": {
            "status": "paid",
            "pay_time": datetime.now()
        }}
    )

    # 增加余额
    user_coll.update_one(
        {"openid": openid},
        {"$inc": {"balance": order["amount"]}},
        upsert=True
    )

    # 如果 >=29.9 自动升VIP
    if order["amount"] >= 29.9:
        user_coll.update_one(
            {"openid": openid},
            {"$set": {
                "member_level": "vip",
                "member_expire": datetime.now() + timedelta(days=90)
            }}
        )

    return {
        "code": 0,
        "msg": "支付成功，余额已到账",
        "data": {
            "order_id": req.order_id,
            "amount": order["amount"]
        }
    }

# ------------------------------
# 3. 查询用户余额/会员（给前端用）
# ------------------------------
@router.get("/user_info")
async def user_info(current_user: User = Depends(get_current_user)):
    user_coll = get_collection("users")
    user = user_coll.find_one({"id": current_user.id})

    if not user:
        return {
            "code": 0,
            "data": {
                "balance": 0,
                "member_level": "normal",
                "member_expire": None
            }
        }

    return {
        "code": 0,
        "data": {
            "balance": user.get("balance", 0),
            "member_level": user.get("member_level", "normal"),
            "member_expire": user.get("member_expire")
        }
    }