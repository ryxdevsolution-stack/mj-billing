import uuid
from datetime import datetime
from flask import g, request
from extensions import db
from models.audit_model import AuditLog

def log_action(action_type, table_name=None, record_id=None, old_data=None, new_data=None):
    """
    Log action to audit_log table with client_id
    MUST be called after any CREATE, UPDATE, DELETE operation
    """
    try:
        # Get client_id from g.user (set by authenticate decorator)
        if not hasattr(g, 'user'):
            return

        client_id = g.user.get('client_id')
        user_id = g.user.get('user_id')

        # Create audit log entry
        audit_entry = AuditLog(
            log_id=str(uuid.uuid4()),
            client_id=client_id,
            user_id=user_id,
            action_type=action_type,
            table_name=table_name,
            record_id=record_id,
            old_data=old_data,
            new_data=new_data,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            timestamp=datetime.utcnow()
        )

        db.session.add(audit_entry)
        db.session.commit()

    except Exception as e:
        # Don't fail the main operation if audit logging fails
        print(f"Audit log error: {str(e)}")
        db.session.rollback()
