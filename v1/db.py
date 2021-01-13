import psycopg2
from psycopg2.extras import RealDictCursor

from classes.bookingSlot import BookingSlot


class DatabaseSession:
    def __init__(self, host, port, user, pwd):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.master_conn = self.createConnection(host, port, user, pwd, 'mosip_master')
        self.kernel_conn = self.createConnection(host, port, user, pwd, 'mosip_kernel')
        self.kernel_conn.autocommit = True
        self.prereg_conn = self.createConnection(host, port, user, pwd, 'mosip_prereg')
        self.prereg_conn.autocommit = True

    @staticmethod
    def createConnection(host, port, user, pwd, db):
        return psycopg2.connect(
            host=host,
            port=port,
            database=db,
            user=user,
            password=pwd
        )

    def getLocation(self):
        cur = self.master_conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("Select code, name, parent_loc_code from location;")
        return cur.fetchall()

    def getGender(self):
        cur = self.master_conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("Select code, name from gender;")
        return cur.fetchall()

    def getResidenceStatus(self):
        cur = self.master_conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("Select code, name from individual_type;")
        return cur.fetchall()

    def getDynamicFields(self):
        cur = self.master_conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("Select name, value_json from dynamic_field;")
        return cur.fetchall()

    def deleteUnAssignedPridFromKernel(self):
        cur = self.kernel_conn.cursor()
        cur.execute("Delete from prid where prid_status = 'UNASSIGNED' or prid_status = 'AVAILABLE';")
        return cur.rowcount

    def getApplication(self, prid):
        cur = self.prereg_conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("Select prereg_id, status_code from applicant_demographic where prereg_id=%s;", [prid])
        return cur.fetchone()

    def appointmentCountByPrid(self, prid):
        cur = self.prereg_conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("Select count(*) from reg_appointment where prereg_id=%s;", [prid])
        return cur.fetchone()['count']

    def checkSlot(self, slot_info: BookingSlot):
        cur = self.prereg_conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
        with appointments as (
            select count(*) as appointments from reg_appointment 
            where regcntr_id=%s and appointment_date=%s and slot_from_time=%s
        )
        select * from reg_available_slot, appointments
        where regcntr_id=%s and availability_date=%s and slot_from_time=%s;
        """, [slot_info.registration_center, slot_info.slot_date, slot_info.slot_time_from,
              slot_info.registration_center, slot_info.slot_date, slot_info.slot_time_from])
        return cur.fetchone()

    def createSlot(self, slot_info: BookingSlot):
        cur = self.prereg_conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            Insert into reg_available_slot (regcntr_id, availability_date, slot_from_time, slot_to_time, 
            available_kiosks, cr_by, cr_dtimes, is_deleted) values (%s, %s, %s, %s, %s, %s, %s, %s);
        """, [slot_info.registration_center, slot_info.slot_date, slot_info.slot_time_from, slot_info.slot_time_to,
              1, 'migration_script', 'now()', 'false'])

    def updateSlot(self, slot_info: BookingSlot, count):
        cur = self.prereg_conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            Update reg_available_slot set available_kiosks=%s where regcntr_id=%s and availability_date=%s and 
                slot_from_time=%s;
        """, [count, slot_info.registration_center, slot_info.slot_date, slot_info.slot_time_from])

    def insertPridToKernel(self, prid):
        cur = self.kernel_conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            insert into prid (prid, prid_status, cr_by, cr_dtimes) 
            values (%s, %s, %s, %s)
        """, [prid, 'AVAILABLE', 'migration_script', 'now()'])

    def updateApplicationStatus(self, prid, status):
        cur = self.prereg_conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            update applicant_demographic set status_code=%s where prereg_id=%s;
        """, [status, prid])

    def updatePreregCreatedBy(self, prid, cr_by):
        cur = self.prereg_conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            update applicant_demographic set cr_appuser_id=%s, cr_by=%s where prereg_id=%s;
        """, [cr_by, cr_by, prid])
