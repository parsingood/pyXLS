
import datetime 
import cx_Oracle

print('Started at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')

cx_Oracle.init_oracle_client(lib_dir = r"C:\app\instantclient_19_19")
dsn_tns = cx_Oracle.makedsn('10.10.21.33', '1521', service_name='opera') # if needed, place an 'r' before any parameter in 

today = datetime.date.today()
TODAY_STR = today.strftime("%d.%m.%Y")

# Свързване към базата данни
connection = cx_Oracle.connect(user=r'opera', password='opera', dsn=dsn_tns) 
cursor = connection.cursor()
# PL/SQL кодът
plsql_block = f"""  
DECLARE
 NEW_RESV_NAME_ID  NUMBER;
 NEW_ISSUE_ID NUMBER;
 OCC  NUMBER;
 --MY_SOURCE_NAME_ID  NUMBER; -- 20.11.2018
 MY_RESULT VARCHAR2(4000);
 NEW_CURRENT_DATE DATE;
 OLD_CURRENT_DATE DATE;
 NEW_DATE_FROM DATE;
 CNT NUMBER;
 GUAR_RESORT_LIST VARCHAR2(1000);
BEGIN
  OLD_CURRENT_DATE := CURRENT_DATE;

FOR X IN (
            select * from TRAIN.ALB_AGENT_GUARANTEES
            WHERE ACTIVE_YN = 'Y'
            AND CURRENT_DATE + TRUNC(RELEASE_DAYS) < DATE_TILL 
            ORDER BY ID
) 
LOOP

  NEW_DATE_FROM :=  TRUNC(CURRENT_DATE,'DD') + TRUNC(X.RELEASE_DAYS);
  
  IF NEW_DATE_FROM < X.DATE_FROM  THEN 
    NEW_DATE_FROM := X.DATE_FROM;
  END IF;
  
  IF X.RELEASE_DAYS > 0 AND X.RELEASE_DAYS < 1 THEN
    IF (CURRENT_DATE - TRUNC(CURRENT_DATE)) >= X.RELEASE_DAYS THEN
      NEW_DATE_FROM := NEW_DATE_FROM + 1;
    END IF;
  END IF;

  NEW_CURRENT_DATE := CURRENT_DATE;
  IF   NEW_CURRENT_DATE <= OLD_CURRENT_DATE + 2 /24/60/60 THEN
      NEW_CURRENT_DATE := OLD_CURRENT_DATE + 2 /24/60/60; 
  END IF;
  OLD_CURRENT_DATE := NEW_CURRENT_DATE;

  SELECT MIN(RESV_NAME_ID)  INTO NEW_RESV_NAME_ID FROM OPERA.RESERVATION_NAME R WHERE R.RESV_NAME_ID=X.RESV_NAME_ID AND R.RESV_STATUS NOT IN ('CANCELLED','NO SHOW');
  
  SELECT  TRAIN.ALB_RESV_ISSUE_ID.NEXTVAL INTO NEW_ISSUE_ID FROM DUAL;
  
  --SELECT MAX(NAME_ID) INTO MY_SOURCE_NAME_ID FROM TRAIN.ALB_NAME_INDEX WHERE SOURCE='Y' AND AGENT = TRAIN.ALB_UDFC21_SO(X.AGENT);
  -- 20.11.2018
  
  INSERT INTO TRAIN.ALB_RESERVATION_SPANS 
  (      ISSUE_ID,    MY_ID, RESERVATION_DATE,  ROOMS           )
  SELECT NEW_ISSUE_ID,    1,       D.THE_DATE
    , CASE WHEN  X.ROOMS > NVL(SUM(R.SOLD),0) THEN X.ROOMS - NVL(SUM(R.SOLD),0)  ELSE 0 END  NOT_SOLD 
    FROM
      (SELECT   LEVEL + NEW_DATE_FROM - 1 THE_DATE FROM DUAL CONNECT BY LEVEL <= X.DATE_TILL - NEW_DATE_FROM + 1 ) D 
    LEFT JOIN 
      ( SELECT Y.RESERVATION_DATE, SUM(Y.PHYSICAL_QUANTITY) SOLD
        FROM
          (
              SELECT E.RESERVATION_DATE,  E.PHYSICAL_QUANTITY -- , E.RESV_DAILY_EL_SEQ
              FROM OPERA.RESERVATION_DAILY_ELEMENTS E 
 --             JOIN OPERA.RESORT$_ROOM_CATEGORY T 
 --               ON T.ROOM_CATEGORY = E.BOOKED_ROOM_CATEGORY   ---  OR MAY BE: E.ROOM_CATEGORY  
 --              AND T.LABEL = X.ROOMTYPE       
              JOIN OPERA.RESERVATION_DAILY_ELEMENT_NAME EN 
                ON EN.RESERVATION_DATE = E.RESERVATION_DATE 
               AND EN.RESORT = X.RESORT 
               AND EN.RESV_DAILY_EL_SEQ = E.RESV_DAILY_EL_SEQ
     --         WHERE EN.SOURCE_ID = MY_SOURCE_NAME_ID  -- 20.11.2018
              WHERE EN.SOURCE_ID IN 
                ( 
                  SELECT NAME_ID FROM TRAIN.ALB_NAME_INDEX I
                  WHERE I.SOURCE='Y' 
                  AND 
                  (    (SUBSTR(X.AGENT,1,1)='@' AND I.MARKET = SUBSTR(X.AGENT,2) 
                        AND I.AGENT IS NOT NULL)
                    OR (TRAIN.ALB_UDFC21_SO(X.AGENT)='BGB' AND I.AGENT LIKE 'BGB%' ) 
                    OR (I.AGENT = TRAIN.ALB_UDFC21_SO(X.AGENT))
                  )
                ) 
               AND ( X.RATE_CODE IS NULL OR NVL(EN.RATE_CODE,'NULL') LIKE X.RATE_CODE ) 
               AND NVL(EN.RATE_CODE,'NULL') <> 'GAR'
               AND E.RESERVATION_DATE BETWEEN NEW_DATE_FROM AND X.DATE_TILL
               AND E.RESORT = X.RESORT 
               AND E.RESV_STATUS   NOT IN ('CANCELLED','NO SHOW')  --'RESERVED' -- NOT IN ('CANCELLED','NO SHOW')
               AND NVL(E.DUE_OUT_YN,'N') = 'N'
               AND E.ROOM_CATEGORY IN   ---  OR MAY BE: E.ROOM_CATEGORY IN -- ---  OR MAY BE: E.BOOKED_ROOM_CATEGORY IN
               (  SELECT ROOM_CATEGORY 
                  FROM OPERA.RESORT$_ROOM_CATEGORY T
                  WHERE T.RESORT = X.RESORT 
                  AND (     ( SUBSTR(X.ROOMTYPE,1,1)='@' 
                              AND T.ROOM_CLASS = 
                                ( SELECT NVL(MAX(ROOM_CLASS),'') 
                                  FROM  OPERA.RESORT$_ROOM_CATEGORY TT
                                  WHERE TT.RESORT = X.RESORT AND LABEL = SUBSTR(X.ROOMTYPE,2) )
                            )
                        OR  ( T.LABEL = X.ROOMTYPE )
                      )
               )
              GROUP BY E.RESERVATION_DATE, E.RESV_DAILY_EL_SEQ, E.PHYSICAL_QUANTITY
          ) Y
          GROUP BY  Y.RESERVATION_DATE
      ) R
    ON D.THE_DATE = R.RESERVATION_DATE
    GROUP BY  D.THE_DATE
  ;  
    
  INSERT INTO TRAIN.ALB_RESERVATIONS (
                MY_ID,
                NEW_TRUNC_BEGIN_DATE,
                NEW_TRUNC_END_DATE,
                NEW_LABEL,
                NEW_BOOKED_LABEL,
                MY_GUEST_LAST_NAME,
                MY_GUEST_FIRST_NAME,
                NEW_RESORT,
                NEW_COUNTRY_CODE,
                MY_ALLOTMENT_CODE,
                NEW_RATE_CODE,
                AD,
                CH1,
                CH2,
                CH3,
                CH4,
                CH5,
                ISSHARED,
                IS_PM,
                IS_RI,
                IS_FO,
                RES_B,
                RES_L,
                RES_D,
                MY_CUSTOM_REFERENCE,
                MY_COMMENT,
                EGN,
                AGENT,
                ISSUE_DATE,
                RESV_NAME_ID,
                CONFIRMATION_NO,
                CH,
                DENY_REASON,
                ACT_RESORT,
                ACT_LABEL,
                AD1,
                AD2,
                DISCOUNT_AMT,
                DISCOUNT_PRCNT,
                BOOK_DATE,
                DISCOUNT_REASON_CODE,
                GUEST_EMAIL,
                GUEST_PHONE,
                APP_USER,
                ISSUE_ID,
                ROOMS,
                MARKET,
                BOARD,
                OTHER,
                GEN_RATE_CODE,
                ALT_RESORT,
                NAME_ID,
                RESV_NO,
                DISCOUNT_REASON,
                ROOM_RESV_ID,
                GUEST_CITY,
                GUEST_ADDRESS,
                GUEST_ZIP,
                UPDATE_RESV_NANE_ID,
                SUB_AGENT )
    SELECT 
                1 MY_ID,
                NEW_DATE_FROM  NEW_TRUNC_BEGIN_DATE,
                X.DATE_TILL NEW_TRUNC_END_DATE,
                (CASE WHEN SUBSTR(X.ROOMTYPE,1,1)='@' THEN SUBSTR(X.ROOMTYPE,2) ELSE X.ROOMTYPE END)  NEW_LABEL,
                (CASE WHEN SUBSTR(X.ROOMTYPE,1,1)='@' THEN SUBSTR(X.ROOMTYPE,2) ELSE X.ROOMTYPE END) NEW_BOOKED_LABEL,
                'BLOCK-' || X.AGENT || '-GUARANTEE' MY_GUEST_LAST_NAME,
                NULL MY_GUEST_FIRST_NAME,
                X.RESORT NEW_RESORT,
                NULL NEW_COUNTRY_CODE,
                NULL MY_ALLOTMENT_CODE,
                'GARXXZZZ' || X.AGENT NEW_RATE_CODE,
                0 AD,
                0 CH1,
                0 CH2,
                0 CH3,
                0 CH4,
                0 CH5,
                NULL ISSHARED,
                NULL IS_PM,
                NULL IS_RI,
                CASE WHEN X.CONFIRMATION_NO IS NULL THEN  'S'  ELSE  'I'  END IS_FO,
--                'I' IS_FO,
                NULL RES_B,
                NULL RES_L,
                NULL RES_D,
                NULL MY_CUSTOM_REFERENCE,
                NULL MY_COMMENT,
                NULL EGN,
                --X.AGENT AGENT,
                --'BLOCK' AGENT,
                'GUARANT' AGENT,
                NEW_CURRENT_DATE ISSUE_DATE,
                CASE WHEN X.CONFIRMATION_NO IS NULL THEN  NULL  ELSE  0  END RESV_NAME_ID,
                CASE WHEN X.CONFIRMATION_NO IS NULL THEN  NULL  ELSE  X.CONFIRMATION_NO  END CONFIRMATION_NO,
                0 CH,
                NULL DENY_REASON,
                NULL ACT_RESORT,
                NULL ACT_LABEL,
                NULL AD1,
                NULL AD2,
                NULL DISCOUNT_AMT,
                NULL DISCOUNT_PRCNT,
                NULL BOOK_DATE,
                NULL DISCOUNT_REASON_CODE,
                NULL GUEST_EMAIL,
                NULL GUEST_PHONE,
                'IVANM' APP_USER,
                NEW_ISSUE_ID ISSUE_ID,
                0 ROOMS,
                NULL MARKET,
                NULL BOARD,
                NULL OTHER,
                NULL GEN_RATE_CODE,
                NULL ALT_RESORT,
                NULL NAME_ID,
                NULL RESV_NO,
                NULL DISCOUNT_REASON,
                NULL ROOM_RESV_ID,
                NULL GUEST_CITY,
                NULL GUEST_ADDRESS,
                NULL GUEST_ZIP,
                NULL UPDATE_RESV_NANE_ID,
                NULL SUB_AGENT          
    FROM DUAL ;

    -- ADD RATE_HEADER IF NOT EXISTS
    select COUNT(*) INTO CNT from OPERA.RATE_HEADER 
    where RESORT = X.RESORT AND  RATE_CODE='GARXXZZZ' || X.AGENT
    ;
    IF CNT = 0 THEN
      TRAIN.ALB_RATE_HEARED_GENERATE
        (
         HOT => X.RESORT
        ,INFO => 'GUARANTEE ROOMS ZERRO RATE'
        ,RATE_MARKET => 'PER'
        ,RATE_SOURCE => NULL
        ,RATE_CAT => 'HU'
        ,RATE_CL  => 'INT'
        ,DATE_FROM => '01.10.2017' 
        ,DATE_TILL => '01.10.2022' 
        ,CURR => 'BGN'
        ,IN_RATE_CODE => 'GARXXZZZ' || X.AGENT
        ,MY_USER => 'IVANM'
        ,MY_MULTIPLICATION => NULL
        )
      ;
    END IF;
    TRAIN.ALB_RESERVATIONS_INTO_OPERA(    MYCOMPANY => '',    MY_AGENT => 'GUARANT',    MY_RESULT => MY_RESULT,    MY_ISSUE_ID => NEW_ISSUE_ID  ); 
  
    UPDATE TRAIN.ALB_AGENT_GUARANTEES G 
    SET CONFIRMATION_NO = (SELECT MAX(CONFIRMATION_NO) FROM TRAIN.ALB_RESERVATIONS S WHERE S.ISSUE_ID=NEW_ISSUE_ID AND S.MY_ID = 1 )
      , RESV_NAME_ID = (SELECT MAX(RESV_NAME_ID) FROM TRAIN.ALB_RESERVATIONS S WHERE S.ISSUE_ID=NEW_ISSUE_ID AND S.MY_ID = 1 )

    WHERE G.ID = X.ID
    AND EXISTS
    (SELECT 1 FROM TRAIN.ALB_RESERVATIONS P WHERE P.ISSUE_ID=NEW_ISSUE_ID AND P.MY_ID = 1 AND P.CONFIRMATION_NO IS NOT NULL )
    ;
   UPDATE TRAIN.ALB_AGENT_GUARANTEES G 
    SET MOMENT = CURRENT_DATE
    WHERE G.ID = X.ID
    ;
    COMMIT
    ;
END LOOP;




end;
"""


# '''
  # SELECT LISTAGG (RESORT,',') WITHIN GROUP(ORDER BY RESORT) INTO GUAR_RESORT_LIST
  # FROM (SELECT RESORT FROM TRAIN.ALB_AGENT_GUARANTEES GROUP BY RESORT)
  # ;
  # TRAIN.ALB_ALLOTMENT_CLEAR_PROCENT(
    # RESORT_LIST => GUAR_RESORT_LIST,
    # AGENT_SO_LIST => NULL,
    # AGENT_TA_LIST => NULL,
    # AGENT_NOT_IN_LIST => NULL,
    # MY_BEGIN_DATE => TO_CHAR(GREATEST (CURRENT_DATE,TO_DATE('250421','DDMMYY')),'DD.MM.YYYY'),
    # MY_END_DATE => TO_CHAR(GREATEST (CURRENT_DATE,TO_DATE('250421','DDMMYY')) + 213 + 300,'DD.MM.YYYY'),
    # REMAIN_PART => 0,
    # CLEAR_PART => 1,
    # MY_ROOM_CLASS => '%',
    # AGENT_ALLOTMENT_CODE => 'GUARANT%'
    # );
# '''


# Изпълнение на PL/SQL блока
cursor.execute(plsql_block)

# Затваряне на курсора и връзката
cursor.close()
connection.close()

print('Finished at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')





