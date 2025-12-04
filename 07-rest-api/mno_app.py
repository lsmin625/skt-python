from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel
import mno_service

app = FastAPI(title="Mobile Plans API")


# ---------- BaseModel 모델 ----------

class PlanBase(BaseModel):
    name: str
    monthly_fee: int
    data_gb: float
    voice_minutes: int
    sms_count: int
    is_unlimited_data: bool


class PlanCreate(PlanBase):
    pass


class PlanUpdate(BaseModel, total=False):
    name: Optional[str]
    monthly_fee: Optional[int]
    data_gb: Optional[float]
    voice_minutes: Optional[int]
    sms_count: Optional[int]
    is_unlimited_data: Optional[bool]


class Plan(PlanBase):
    plan_id: int
    created_at: Optional[str]

    class Config:
        orm_mode = True


class BenefitBase(BaseModel):
    benefit_name: str
    benefit_desc: Optional[str]
    priority: Optional[int]


class BenefitCreate(BenefitBase):
    pass


class Benefit(BenefitBase):
    benefit_id: int
    plan_id: int

    class Config:
        orm_mode = True


class PlanWithBenefits(Plan):
    benefits: list[Benefit]


# ---------- Startup ----------

@app.on_event("startup")
def on_startup():
    mno_service.init_db()


# ---------- Plan REST API ----------

@app.post("/plans", response_model=Plan)
def create_plan_api(plan: PlanCreate):
    """새 요금제 생성"""
    try:
        plan_id = mno_service.create_plan(
            name=plan['name'],
            monthly_fee=plan['monthly_fee'],
            data_gb=plan['data_gb'],
            voice_minutes=plan['voice_minutes'],
            sms_count=plan['sms_count'],
            is_unlimited_data=plan.get('is_unlimited_data', False),
        )
        result = mno_service.get_plan(plan_id)
        if not result:
            raise HTTPException(status_code=500, detail="Plan creation failed")
        return Plan(**dict(zip(['plan_id', 'name', 'monthly_fee', 'data_gb', 'voice_minutes', 'sms_count', 'is_unlimited_data', 'created_at'], result)))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/plans", response_model=list[Plan])
def list_plans():
    """모든 요금제 조회"""
    rows = mno_service.get_all_plans()
    result = []
    for row in rows:
        plan_dict = dict(zip(['plan_id', 'name', 'monthly_fee', 'data_gb', 'voice_minutes', 'sms_count', 'is_unlimited_data', 'created_at'], row))
        result.append(Plan(**plan_dict))
    return result


@app.get("/plans/{plan_id}", response_model=Plan)
def get_plan_api(plan_id: int):
    """특정 요금제 조회"""
    row = mno_service.get_plan(plan_id)
    if not row:
        raise HTTPException(status_code=404, detail="Plan not found")
    plan_dict = dict(zip(['plan_id', 'name', 'monthly_fee', 'data_gb', 'voice_minutes', 'sms_count', 'is_unlimited_data', 'created_at'], row))
    return Plan(**plan_dict)


@app.patch("/plans/{plan_id}", response_model=Plan)
def update_plan_api(plan_id: int, plan_update: PlanUpdate):
    """요금제 정보 부분 업데이트 (현재는 monthly_fee만 지원)"""
    if 'monthly_fee' in plan_update and plan_update['monthly_fee'] is not None:
        success = mno_service.update_plan_fee(plan_id, plan_update['monthly_fee'])
        if not success:
            raise HTTPException(status_code=404, detail="Plan not found")
    
    row = mno_service.get_plan(plan_id)
    if not row:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    plan_dict = dict(zip(['plan_id', 'name', 'monthly_fee', 'data_gb', 'voice_minutes', 'sms_count', 'is_unlimited_data', 'created_at'], row))
    return Plan(**plan_dict)


@app.delete("/plans/{plan_id}")
def delete_plan_api(plan_id: int):
    """요금제 삭제"""
    success = mno_service.delete_plan(plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return {"message": "Plan deleted"}


# ---------- Benefit REST API ----------

@app.post("/plans/{plan_id}/benefits", response_model=Benefit)
def create_benefit_api(plan_id: int, benefit: BenefitCreate):
    """요금제 혜택 추가"""
    # plan 존재 여부 확인
    plan = mno_service.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    benefit_id = mno_service.create_plan_benefit(
        plan_id=plan_id,
        benefit_name=benefit['benefit_name'],
        benefit_desc=benefit.get('benefit_desc'),
        priority=benefit.get('priority'),
    )
    
    # benefit_id를 사용하여 생성된 혜택 조회 (간단하게 입력값 반환)
    return Benefit(
        benefit_id=benefit_id,
        plan_id=plan_id,
        benefit_name=benefit['benefit_name'],
        benefit_desc=benefit.get('benefit_desc'),
        priority=benefit.get('priority')
    )


@app.get("/plans/{plan_id}/benefits", response_model=list[Benefit])
def list_benefits_api(plan_id: int):
    """특정 요금제의 모든 혜택 조회"""
    plan, benefits = mno_service.get_plan_with_benefits(plan_id)
    if not plan:
        return []
    
    result = []
    for row in benefits:
        benefit_dict = dict(zip(['benefit_id', 'benefit_name', 'benefit_desc', 'priority'], row))
        benefit_dict['plan_id'] = plan_id
        result.append(Benefit(**benefit_dict))
    return result


@app.get("/plans/{plan_id}/details", response_model=PlanWithBenefits)
def get_plan_with_benefits_api(plan_id: int):
    """요금제와 혜택 정보를 함께 조회"""
    plan, benefits = mno_service.get_plan_with_benefits(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # plan을 dict로 변환
    plan_dict = dict(zip(['plan_id', 'name', 'monthly_fee', 'data_gb', 'voice_minutes', 'sms_count', 'is_unlimited_data', 'created_at'], plan))
    
    # benefits를 list of dict로 변환
    benefits_list = []
    for row in benefits:
        benefit_dict = dict(zip(['benefit_id', 'benefit_name', 'benefit_desc', 'priority'], row))
        benefit_dict['plan_id'] = plan_id
        benefits_list.append(Benefit(**benefit_dict))
    
    plan_dict['benefits'] = benefits_list
    return PlanWithBenefits(**plan_dict)
