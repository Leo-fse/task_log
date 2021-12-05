# 標準モジュール
import os
# サードパーティモジュール
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic.types import PositiveInt
import pandas as pd

# オリジナル
from input.nzl_hinemei_info import NZL_HINMEI_DICT
from tasks.connect_db import mongo
from decolog.decolog import log, get_logger
logger = get_logger()
SQL_FILE_PATH = "tasks/gcode_main_info/sql"


class GcodeMainInfo(BaseModel):
    MODEL: str = Field(..., title="型式", min_length=1)
    DESIGN_MODEL: str = Field(..., title="設計型式", min_length=1)
    PARTS_TYPE: str = Field(..., title="部品名称（略）", min_length=3, max_length=3)
    FC_GCODE: str = Field(..., title="Gコード", min_length=9, max_length=9)
    HINMEI: str = Field(..., title="部品名称", min_length=1,
                        description="承認済みの最新リバイスNo")
    USE_KBN: str = Field(..., title="使用区分", min_length=1)
    IS_STANDARD: bool = Field(..., title="標準品か否か")
    REV_NO: PositiveInt = Field(..., title="リバイスNo")
    INSERT_DATE: datetime = Field(..., title="MONGODBへの保存日時")


@log(logger)
def _fetch_active_gcode_from_ahopss():
    """
    AHOPSSのTB_GC_MAINおよびTB_GC_APPLOVALより
    承認済み最新リバイスのデータを取得する。
    SQLにて、機種および部品を絞り込みデータ取得。
    ============================================================
    取得対象機種：[501D, 501F, 701D, 701F, 501G, 701G, 501J, 701J]
    取得対象部品：[NZL, BAS, TRA, TRS, TS[1234], TC[1234], RS[1234]]
    """

    def is_standard():
        """
        標準品かどうかの判定。
        - NZL、TRSの場合：全て標準品
        - それ以外の場合：　使用区分が[STD, STDA]の場合標準品
        """
        return True

    def get_Hinmei(PARTS_TYPE, HINMEI):
        """
        NZLの細分化用：ノズルをトップハットやパイロットノズル等に分ける
        NZL以外についてはそのままの分類を返す
        """
        if PARTS_TYPE == "NZL":
            return NZL_HINMEI_DICT.get(HINMEI, "未登録")
        else:
            return HINMEI

    file_name = 'active_gcode.sql'
    with open(os.path.join(SQL_FILE_PATH, file_name)) as f:
        SQL = f.read()
    return False


@log(logger)
def _fetch_installing_gcode_from_lcs():
    """
    LCSから、Gコード毎の現装着ユニット数及び、ユニット名称を取得する。
    SQLにて、機種、部品および部品ステータスの絞り込みを実施する
    ============================================================
    取得対象機種    :[501D, 501F, 701D, 701F, 501G, 701G, 501J, 701J]
    取得対象部品    :[NZL, BAS, TRA, TRS, TS[1234], TC[1234], RS[1234]]
    部品ステータス  :0920（サイト運転中）
    シリアル最新    : 1(True)
    """
    file_name = 'installing_data.sql'
    with open(os.path.join(SQL_FILE_PATH, file_name)) as f:
        SQL = f.read()
    return False


@log(logger)
def _fetch_zaiko_amount_from_lcs_and_logitics():
    """
    LCS及び在庫システムより、在庫情報を取得する。
    SQLにて、機種および部品を絞り込みデータ取得。
    ============================================================
    取得対象機種：[501D, 501F, 701D, 701F, 501G, 701G, 501J, 701J]
    取得対象部品：[NZL, BAS, TRA, TRS, TS[1234], TC[1234], RS[1234]]
    """
    return False


@log(logger)
def _save_to_mongodb(db_name, collection_name, data: list[GcodeMainInfo]):
    mongo.save_data(db_name, collection_name, isDel=True)


def main():
    """
    各種情報を取得、マージした後にMONGODBに保存
    """
    main_gcode_info = _fetch_active_gcode_from_ahopss()
    installing_amount_and_unit = _fetch_installing_gcode_from_lcs()
    zaiko_amount = _fetch_zaiko_amount_from_lcs_and_logitics()

    if all([main_gcode_info, installing_amount_and_unit, zaiko_amount]):
        # 装着数量をマージ
        GCODE_MAIN_INFO = pd.merge(
            main_gcode_info, installing_amount_and_unit,
            how="left", left_on=['FC_GCODE'], right_on=['HOTPARTS_CODE']
        )

        # 在庫情報をマージ
        GCODE_MAIN_INFO = pd.merge(
            GCODE_MAIN_INFO, zaiko_amount,
            how="left", left_on='FC_GCODE', right_on=['HOTPARTS_CODE']
        )

        GCODE_MAIN_INFO["INSERT_DATE"] = datetime.now()
        _save_to_mongodb("MHI", "AHOPSS", "MAIN_GCODE_INFO", GCODE_MAIN_INFO)
    else:
        pass

# data = {
#     "FC_GCODE": "G7FQTRAB7",
#     "REV_NO": 1,
#     "MODEL": "701F",
#     "DESIGN_MODEL": "701F改3",
#     "PARTS_TYPE": "str",
#     "USE_KBN": "str",
#     "HINMEI": "str",
#     "IS_STANDARD": True,
# }


# a = ActiveGcode(**data)
# print(a)
