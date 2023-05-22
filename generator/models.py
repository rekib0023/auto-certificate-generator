from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class CertificateModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    certificate_number = db.Column(db.String(80), unique=True, nullable=False)
    status = db.Column(db.String(120), nullable=True, default="Pending")
    s3_path = db.Column(db.String(256), nullable=True, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Certificate {self.certificate_number}>"
