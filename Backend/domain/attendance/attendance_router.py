from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from starlette import status
from datetime import date, datetime
import holidays

from database import get_db
from domain.attendance import attendance_crud, attendance_schema
from domain.user.user_router import get_current_user
from models import User

import lib.const as const

router = APIRouter(
    prefix="/api/attendance",
)


@router.get("/attendance", 
            description="출석을 합니다.", 
            status_code=status.HTTP_200_OK, 
            tags=["Attendance"])
async def check_attendance(db: Session = Depends(get_db), 
                     current_user: User = Depends(get_current_user)):
    today = date.today()
    weekday = today.weekday()
    if weekday == 5 or weekday == 6:
        raise HTTPException(status_code=400, detail="주말에는 출석을 할 수 없습니다.")

    kr_holidays = holidays.KR()
    if today in kr_holidays:
        raise HTTPException(status_code=400, detail="공휴일에는 출석을 할 수 없습니다.")
    
    check_present_time = attendance_crud.caculate_attendance_time(const.PRESENT_START, const.PRESENT_END)
    check_late_time = attendance_crud.caculate_attendance_time(const.PRESENT_END, const.LATE_END)
    if not check_present_time and not check_late_time:
        raise HTTPException(status_code=400, detail="현재 시간에는 출석을 할 수 없습니다.")
    
    user_exists = attendance_crud.get_existing_user(db, current_user.user_id)
    if not user_exists:
        raise HTTPException(status_code=400, detail="사용자가 존재하지 않습니다.")
    
    count = attendance_crud.get_attendance_count(db, current_user.user_id, date.today())
    if count != 0:
        raise HTTPException(status_code=400, detail="출석은 하루에 한번만 할 수 있습니다.")
    
    if check_present_time:
        attendance_crud.attendance_check(db=db, check_attendance=current_user, state="present")
        return {"message" : "출석"}
    elif check_late_time:
        attendance_crud.attendance_check(db=db, check_attendance=current_user, state="late")
        return {"message" : "지각"}
    

@router.get("/attendance_for_online", 
            description="온라인 유저의 출석을 합니다.", 
            status_code=status.HTTP_200_OK, 
            tags=["Attendance"])
async def check_attendance(db: Session = Depends(get_db), 
                     current_user: User = Depends(get_current_user)):

    if current_user.attendance_type:
        raise HTTPException(status_code=400, detail="온라인 유저만 출석할 수 있습니다.")
    
    today = date.today()
    weekday = today.weekday()
    if weekday == 5 or weekday == 6:
        raise HTTPException(status_code=400, detail="주말에는 출석을 할 수 없습니다.")

    kr_holidays = holidays.KR()
    if today in kr_holidays:
        raise HTTPException(status_code=400, detail="공휴일에는 출석을 할 수 없습니다.")
    
    check_present_time = attendance_crud.caculate_attendance_time(const.PRESENT_START, const.PRESENT_END)
    check_late_time = attendance_crud.caculate_attendance_time(const.PRESENT_END, const.LATE_END)
    if not check_present_time and not check_late_time:
        raise HTTPException(status_code=400, detail="현재 시간에는 출석을 할 수 없습니다.")
    
    user_exists = attendance_crud.get_existing_user(db, current_user.user_id)
    if not user_exists:
        raise HTTPException(status_code=400, detail="사용자가 존재하지 않습니다.")
    
    count = attendance_crud.get_attendance_count(db, current_user.user_id, date.today())
    if count != 0:
        raise HTTPException(status_code=400, detail="출석은 하루에 한번만 할 수 있습니다.")
    
    if check_present_time:
        attendance_crud.attendance_check(db=db, check_attendance=current_user, state="present")
        return {"message" : "출석"}
    elif check_late_time:
        attendance_crud.attendance_check(db=db, check_attendance=current_user, state="late")
        return {"message" : "지각"}


@router.get("/all_list", 
            description="모든 출석 현황을 조회합니다.", 
            response_model=list[attendance_schema.Attendance], 
            tags=["Attendance"])
async def get_attendance_all_list(db: Session = Depends(get_db), 
                  current_user: User = Depends(get_current_user)):
    _attendance_list = attendance_crud.get_all_attendance_list(db)
    return _attendance_list


@router.get("/user_attendance/{username}", 
            description="해당 유저의 출석 기록을 조회합니다.", 
            response_model=list[attendance_schema.Attendance], 
            tags=["Attendance"])
async def get_user_attendance(db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    user_attendance_list = attendance_crud.get_user_attendance_list(db, current_user.user_id)
    return user_attendance_list


@router.get("/today_user_attendance/{username}", 
            description="해당 유저의 오늘 출석 기록을 조회합니다.", 
            response_model=list[attendance_schema.Attendance], 
            tags=["Attendance"])
async def get_user_attendance(db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    user_attendance_list = attendance_crud.get_today_user_attendance_list(db, current_user.user_id)
    return user_attendance_list


@router.get("/attendance_stats/{username}", 
            description="해당 유저의 출석(present), 지각(late), 결석(absent) 횟수와 벌금을 계산합니다.", 
            tags=["Attendance"])
async def get_attendance_stats(db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    stats = attendance_crud.calculate_attendance_stats(db, current_user.user_id)
    return stats


@router.get("/fine_ranking", 
            description="전체 유저의 벌금을 계산하고 높을 순서데로 정렬합니다.", 
            tags=["Attendance"])
async def get_all_attendance_stats(db: Session = Depends(get_db), 
                             current_user: User = Depends(get_current_user)):
    return attendance_crud.calculate_all_users_attendance_stats(db)


@router.get("/daily_attendance", 
            description="해당 날짜의 모든 유저의 출석 상태를 조회합니다.", 
            tags=["Attendance"])
async def get_daily_attendance(attendance_date: date = Query(..., description="The date to check the attendance for"),
                         db: Session = Depends(get_db), 
                         current_user: User = Depends(get_current_user)):
    attendance_stats = attendance_crud.get_daily_attendance_stats(db, attendance_date)
    return attendance_stats