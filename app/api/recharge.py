from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.db.mongo import get_collection

router = APIRouter(prefix="/recharge", tags=["充值模块"])

# ------------------------------
# 数据模型
# ------------------------------
class CreateOrderRequest(BaseModel):
    openid: str
    amount: float

class PayRequest(BaseModel):
    order_id: str
    openid: str

# ------------------------------
# 1. 创建充值订单
# ------------------------------
@router.post("/create_order")
async def create_order(req: CreateOrderRequest):
    coll = get_collection("recharge_orders")

    order = {
        "openid": req.openid,
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
async def pay(req: PayRequest):
    order_coll = get_collection("recharge_orders")
    user_coll = get_collection("users")

    # 查找订单
    order = order_coll.find_one({"_id": req.order_id})
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
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
        {"openid": req.openid},
        {"$inc": {"balance": order["amount"]}},
        upsert=True
    )

    # 如果 >=29.9 自动升VIP
    if order["amount"] >= 29.9:
        user_coll.update_one(
            {"openid": req.openid},
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
async def user_info(openid: str):
    user_coll = get_collection("users")
    user = user_coll.find_one({"openid": openid})

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