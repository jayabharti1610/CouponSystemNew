from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import text

db = SQLAlchemy()

class Coupon(db.Model):
    __tablename__ = 'coupons'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    discount_type = db.Column(db.String, nullable=False)  # 'percentage', 'fixed_amount', 'minimum_spend'
    discount_value = db.Column(db.Numeric(10, 2), nullable=False)
    minimum_spend = db.Column(db.Numeric(10, 2))
    expiry_date = db.Column(db.DateTime(timezone=True), nullable=False)
    is_used = db.Column(db.Boolean, nullable=False, default=False)
    used_at = db.Column(db.DateTime(timezone=True))
    qr_code_data = db.Column(db.Text)
    short_url = db.Column(db.String, unique=True)
    assigned_to_email = db.Column(db.String)
    is_assigned = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    referrals_as_coupon = db.relationship('Referral', foreign_keys='Referral.coupon_id', backref='coupon')
    referrals_as_reward = db.relationship('Referral', foreign_keys='Referral.referrer_reward_coupon_id', backref='reward_coupon')

    def __repr__(self):
        return f'<Coupon {self.code}>'
    
    @property
    def is_expired(self):
        return datetime.utcnow() > self.expiry_date
    
    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired
    
    @property
    def discount_display(self):
        if self.discount_type == 'percentage':
            return f"{self.discount_value}%"
        else:
            return f"${self.discount_value}"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'discount_type': self.discount_type,
            'discount_value': float(self.discount_value),
            'minimum_spend': float(self.minimum_spend) if self.minimum_spend else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'is_used': self.is_used,
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'qr_code_data': self.qr_code_data,
            'short_url': self.short_url,
            'assigned_to_email': self.assigned_to_email,
            'is_assigned': self.is_assigned,
            'is_expired': self.is_expired,
            'is_valid': self.is_valid,
            'discount_display': self.discount_display,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Referral(db.Model):
    __tablename__ = 'referrals'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referrer_email = db.Column(db.String, nullable=False)
    referee_email = db.Column(db.String, nullable=False)
    coupon_id = db.Column(UUID(as_uuid=True), db.ForeignKey('coupons.id'))
    
    # Manual discount control
    discount_applied = db.Column(db.Numeric, nullable=False)
    discount_type = db.Column(db.String, nullable=False, default='fixed')
    
    # Referrer reward system
    referrer_gets_reward = db.Column(db.Boolean, nullable=False, default=False)
    referrer_reward_coupon_id = db.Column(UUID(as_uuid=True), db.ForeignKey('coupons.id'))
    referrer_reward_value = db.Column(db.Numeric)
    
    # Tracking
    redeemed_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Optional notes for manual decisions
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Referral {self.referrer_email} -> {self.referee_email}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'referrer_email': self.referrer_email,
            'referee_email': self.referee_email,
            'coupon_id': str(self.coupon_id) if self.coupon_id else None,
            'discount_applied': float(self.discount_applied),
            'discount_type': self.discount_type,
            'referrer_gets_reward': self.referrer_gets_reward,
            'referrer_reward_coupon_id': str(self.referrer_reward_coupon_id) if self.referrer_reward_coupon_id else None,
            'referrer_reward_value': float(self.referrer_reward_value) if self.referrer_reward_value else None,
            'redeemed_at': self.redeemed_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'notes': self.notes
        }


class ShopifyConfig(db.Model):
    __tablename__ = 'shopify_configs'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    store_name = db.Column(db.String, unique=True, nullable=False)
    api_key = db.Column(db.String)
    api_secret = db.Column(db.String)
    access_token = db.Column(db.String, nullable=False)
    webhook_secret = db.Column(db.String)
    is_connected = db.Column(db.Boolean, default=False)
    last_sync = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ShopifyConfig {self.store_name}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'store_name': self.store_name,
            'is_connected': self.is_connected,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class ShopifyOrder(db.Model):
    __tablename__ = 'shopify_orders'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shopify_order_id = db.Column(db.String, unique=True, nullable=False)
    order_name = db.Column(db.String, nullable=False)
    customer_email = db.Column(db.String)
    total_price = db.Column(db.Numeric(10, 2))
    order_date = db.Column(db.DateTime(timezone=True))
    discount_codes = db.Column(JSONB)
    customer_data = db.Column(JSONB)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ShopifyOrder {self.order_name}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'shopify_order_id': self.shopify_order_id,
            'order_name': self.order_name,
            'customer_email': self.customer_email,
            'total_price': float(self.total_price) if self.total_price else None,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'discount_codes': self.discount_codes,
            'customer_data': self.customer_data,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class CouponUsageTracking(db.Model):
    __tablename__ = 'coupon_usage_tracking'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coupon_code = db.Column(db.String, unique=True, nullable=False)
    usage_count = db.Column(db.Integer, default=0)
    total_discount = db.Column(db.Numeric(10, 2), default=0)
    last_used = db.Column(db.DateTime(timezone=True))
    orders_data = db.Column(JSONB)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CouponUsageTracking {self.coupon_code}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'coupon_code': self.coupon_code,
            'usage_count': self.usage_count,
            'total_discount': float(self.total_discount),
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'orders_data': self.orders_data,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
