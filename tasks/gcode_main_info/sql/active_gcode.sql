WITH TB_GC_MAIN as (
    SELECT
        FC_GCODE,
        FI_REV_NO
    FROM
        TB_GC_MAIN
    WHERE
        (FC_DELETE_FLG <> 1 and FC_DELETE_FLG is null)
        AND
        FC_GTMODEL
            in
                ('501D', '501F', '701D', '701F', '501G', '701G', '501J', '701J')
        AND
        FC_PARTS_TYPE
            in
                ("NZL", "BAS", "TRA", "TRS", "TS1", "TS2", ".......")
),
TB_GC_APPROVAL as (
    SELECT
        *
    FROM
        TB_GC_APPROVAL
    WHERE
        FC_STATUS = 1
        AND
        (FC_ABOLISHED <> 1 and FC_ABOLISHED is null)
)
