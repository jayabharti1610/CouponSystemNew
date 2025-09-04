from supabase import create_client, Client
from flask import current_app
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import uuid
import secrets
import string

class SupabaseService:
    def __init__(self):
        self.client: Optional[Client] = None
    
    def init_app(self, app):
        """Initialize Supabase client with Flask app"""
        try:
            supabase_url = app.config.get('SUPABASE_URL')
            supabase_key = app.config.get('SUPABASE_KEY')
            
            if not supabase_url or not supabase_key:
                app.logger.warning("Supabase credentials not provided")
                return
            
            self.client = create_client(supabase_url, supabase_key)
            app.logger.info("Supabase client initialized successfully")
        except Exception as e:
            app.logger.error(f"Failed to initialize Supabase client: {str(e)}")
    
    def get_client(self) -> Client:
        """Get the Supabase client"""
        if not self.client:
            raise ValueError("Supabase client not initialized")
        return self.client
    
    def generate_coupon_code(self, length: int = 8) -> str:
        """Generate a random coupon code"""
        characters = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    # Coupon operations (updated for your schema)
    def get_all_coupons(self) -> List[Dict[str, Any]]:
        """Get all coupons from Supabase"""
        try:
            response = self.client.table('coupons').select('*').order('created_at', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            current_app.logger.error(f"Error fetching coupons: {str(e)}")
            return []
    
    def get_coupon_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Get a coupon by its code"""
        try:
            response = self.client.table('coupons').select('*').eq('code', code.upper()).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            current_app.logger.error(f"Error fetching coupon by code {code}: {str(e)}")
            return None
    
    def get_coupon_by_id(self, coupon_id: str) -> Optional[Dict[str, Any]]:
        """Get a coupon by its ID"""
        try:
            response = self.client.table('coupons').select('*').eq('id', coupon_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            current_app.logger.error(f"Error fetching coupon by ID {coupon_id}: {str(e)}")
            return None
    
    def get_coupons_by_email(self, email: str) -> List[Dict[str, Any]]:
        """Get coupons assigned to a specific email"""
        try:
            response = (self.client.table('coupons')
                       .select('*')
                       .eq('assigned_to_email', email.lower())
                       .execute())
            return response.data if response.data else []
        except Exception as e:
            current_app.logger.error(f"Error fetching coupons for email {email}: {str(e)}")
            return []
    
    def create_coupon(self, coupon_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new coupon"""
        try:
            # Add default values based on your schema
            coupon_data.update({
                'id': str(uuid.uuid4()),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            })
            
            # Ensure code is uppercase
            if 'code' in coupon_data:
                coupon_data['code'] = coupon_data['code'].upper()
                
            response = self.client.table('coupons').insert(coupon_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            current_app.logger.error(f"Error creating coupon: {str(e)}")
            return None
    
    def update_coupon(self, coupon_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a coupon"""
        try:
            updates['updated_at'] = datetime.utcnow().isoformat()
            response = (self.client.table('coupons')
                       .update(updates)
                       .eq('id', coupon_id)
                       .execute())
            return response.data[0] if response.data else None
        except Exception as e:
            current_app.logger.error(f"Error updating coupon {coupon_id}: {str(e)}")
            return None
    
    def mark_coupon_used(self, coupon_code: str) -> bool:
        """Mark a coupon as used"""
        try:
            updates = {
                'is_used': True,
                'used_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            response = (self.client.table('coupons')
                       .update(updates)
                       .eq('code', coupon_code.upper())
                       .execute())
            return len(response.data) > 0
        except Exception as e:
            current_app.logger.error(f"Error marking coupon {coupon_code} as used: {str(e)}")
            return False
    
    def delete_coupon(self, coupon_id: str) -> bool:
        """Delete a coupon"""
        try:
            response = self.client.table('coupons').delete().eq('id', coupon_id).execute()
            return True  # Supabase delete doesn't return data, but no exception means success
        except Exception as e:
            current_app.logger.error(f"Error deleting coupon {coupon_id}: {str(e)}")
            return False
    
    def toggle_coupon_status(self, coupon_id: str, new_status: str) -> bool:
        """Toggle coupon active/inactive status"""
        try:
            # Map status to is_used field (inactive = used for UI purposes)
            is_used = new_status == 'inactive'
            updates = {
                'is_used': is_used,
                'updated_at': datetime.utcnow().isoformat()
            }
            response = (self.client.table('coupons')
                       .update(updates)
                       .eq('id', coupon_id)
                       .execute())
            return len(response.data) > 0
        except Exception as e:
            current_app.logger.error(f"Error toggling coupon status {coupon_id}: {str(e)}")
            return False
    
    # Referral operations (updated for your schema)
    def create_referral(self, referral_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new referral"""
        try:
            referral_data.update({
                'id': str(uuid.uuid4()),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            })
            
            response = self.client.table('referrals').insert(referral_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            current_app.logger.error(f"Error creating referral: {str(e)}")
            return None
    
    def get_referrals_by_email(self, email: str, as_referrer: bool = True) -> List[Dict[str, Any]]:
        """Get referrals by email (as referrer or referee)"""
        try:
            field = 'referrer_email' if as_referrer else 'referee_email'
            response = (self.client.table('referrals')
                       .select('*')
                       .eq(field, email.lower())
                       .execute())
            return response.data if response.data else []
        except Exception as e:
            current_app.logger.error(f"Error fetching referrals for {email}: {str(e)}")
            return []
    
    # Shopify operations (updated for your schema)
    def get_shopify_config(self, store_name: str) -> Optional[Dict[str, Any]]:
        """Get Shopify configuration for a store"""
        try:
            response = (self.client.table('shopify_configs')
                       .select('*')
                       .eq('store_name', store_name)
                       .execute())
            return response.data[0] if response.data else None
        except Exception as e:
            current_app.logger.error(f"Error fetching Shopify config for {store_name}: {str(e)}")
            return None
    
    def save_shopify_config(self, config_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Save or update Shopify configuration"""
        try:
            config_data.update({
                'id': str(uuid.uuid4()),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            })
            
            # Try to update first
            existing = self.get_shopify_config(config_data['store_name'])
            if existing:
                del config_data['id']  # Don't update ID
                del config_data['created_at']  # Don't update created_at
                response = (self.client.table('shopify_configs')
                           .update(config_data)
                           .eq('store_name', config_data['store_name'])
                           .execute())
            else:
                # Create new
                response = self.client.table('shopify_configs').insert(config_data).execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            current_app.logger.error(f"Error saving Shopify config: {str(e)}")
            return None
    
    def save_shopify_order(self, order_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Save a Shopify order"""
        try:
            order_data.update({
                'id': str(uuid.uuid4()),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            })
            
            response = self.client.table('shopify_orders').insert(order_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            current_app.logger.error(f"Error saving Shopify order: {str(e)}")
            return None
    
    def update_coupon_usage_tracking(self, coupon_code: str, order_data: Dict[str, Any]) -> bool:
        """Update coupon usage tracking"""
        try:
            # Get existing tracking data
            existing = (self.client.table('coupon_usage_tracking')
                       .select('*')
                       .eq('coupon_code', coupon_code.upper())
                       .execute())
            
            if existing.data:
                # Update existing record
                current_data = existing.data[0]
                new_usage_count = current_data['usage_count'] + 1
                new_total_discount = float(current_data['total_discount']) + float(order_data.get('discount_amount', 0))
                
                updates = {
                    'usage_count': new_usage_count,
                    'total_discount': new_total_discount,
                    'last_used': datetime.utcnow().isoformat(),
                    'orders_data': order_data,
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                response = (self.client.table('coupon_usage_tracking')
                           .update(updates)
                           .eq('coupon_code', coupon_code.upper())
                           .execute())
            else:
                # Create new record
                tracking_data = {
                    'id': str(uuid.uuid4()),
                    'coupon_code': coupon_code.upper(),
                    'usage_count': 1,
                    'total_discount': float(order_data.get('discount_amount', 0)),
                    'last_used': datetime.utcnow().isoformat(),
                    'orders_data': order_data,
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                response = self.client.table('coupon_usage_tracking').insert(tracking_data).execute()
            
            return True  # Success if no exception
        except Exception as e:
            current_app.logger.error(f"Error updating coupon usage tracking for {coupon_code}: {str(e)}")
            return False
    
    # Analytics operations (updated for your schema)
    def get_coupon_analytics(self) -> Dict[str, Any]:
        """Get coupon analytics data"""
        try:
            # Get all coupons
            all_coupons = self.get_all_coupons()
            
            if not all_coupons:
                return {
                    'total_coupons': 0,
                    'active_coupons': 0,
                    'used_coupons': 0,
                    'expired_coupons': 0,
                    'total_value': 0,
                    'gift_coupons': 0,
                    'referral_coupons': 0,
                    'gift_redemption_rate': 0,
                    'referral_redemption_rate': 0,
                    'overall_redemption_rate': 0
                }
            
            now = datetime.utcnow()
            total_coupons = len(all_coupons)
            
            # Count different types of coupons
            used_coupons = 0
            active_coupons = 0
            expired_coupons = 0
            total_value = 0
            
            # Get referral coupon IDs
            try:
                referrals = self.client.table('referrals').select('coupon_id').execute()
                referral_coupon_ids = set(r['coupon_id'] for r in (referrals.data or []) if r.get('coupon_id'))
            except:
                referral_coupon_ids = set()
            
            gift_coupons_count = 0
            referral_coupons_count = 0
            gift_used = 0
            referral_used = 0
            
            for coupon in all_coupons:
                is_referral = coupon['id'] in referral_coupon_ids
                
                if is_referral:
                    referral_coupons_count += 1
                    if coupon.get('is_used'):
                        referral_used += 1
                else:
                    gift_coupons_count += 1
                    if coupon.get('is_used'):
                        gift_used += 1
                
                if coupon.get('is_used'):
                    used_coupons += 1
                else:
                    # Check if expired
                    if coupon.get('expiry_date'):
                        try:
                            expiry_str = coupon['expiry_date']
                            if expiry_str.endswith('Z'):
                                expiry_date = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
                            else:
                                expiry_date = datetime.fromisoformat(expiry_str)
                            
                            if expiry_date <= now:
                                expired_coupons += 1
                            else:
                                active_coupons += 1
                                total_value += float(coupon.get('discount_value', 0))
                        except:
                            active_coupons += 1
                            total_value += float(coupon.get('discount_value', 0))
                    else:
                        active_coupons += 1
                        total_value += float(coupon.get('discount_value', 0))
            
            # Calculate redemption rates
            gift_redemption_rate = (gift_used / gift_coupons_count * 100) if gift_coupons_count > 0 else 0
            referral_redemption_rate = (referral_used / referral_coupons_count * 100) if referral_coupons_count > 0 else 0
            overall_redemption_rate = (used_coupons / total_coupons * 100) if total_coupons > 0 else 0
            
            return {
                'total_coupons': total_coupons,
                'active_coupons': active_coupons,
                'used_coupons': used_coupons,
                'expired_coupons': expired_coupons,
                'total_value': round(total_value, 2),
                'gift_coupons': gift_coupons_count,
                'referral_coupons': referral_coupons_count,
                'gift_redemption_rate': round(gift_redemption_rate, 1),
                'referral_redemption_rate': round(referral_redemption_rate, 1),
                'overall_redemption_rate': round(overall_redemption_rate, 1)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error fetching coupon analytics: {str(e)}")
            return {
                'total_coupons': 0,
                'active_coupons': 0,
                'used_coupons': 0,
                'expired_coupons': 0,
                'total_value': 0,
                'gift_coupons': 0,
                'referral_coupons': 0,
                'gift_redemption_rate': 0,
                'referral_redemption_rate': 0,
                'overall_redemption_rate': 0
            }
    
    # Gift coupon creation
    def create_gift_coupon(self, recipient_email: str, sender_email: str, 
                          name: str, discount_type: str, discount_value: float,
                          expiry_date: str, description: str = None, 
                          minimum_spend: float = None) -> Dict[str, Any]:
        """Create a gift coupon"""
        try:
            coupon_code = self.generate_coupon_code()
            
            # Generate QR code data and short URL
            qr_code_data = f"https://skinandwicks.com/claim/{coupon_code}"
            short_url = f"https://swicks.co/{coupon_code[:6]}"

            coupon_data = {
                'code': coupon_code,
                'name': name,
                'description': description,
                'discount_type': discount_type,
                'discount_value': discount_value,
                'minimum_spend': minimum_spend,
                'expiry_date': expiry_date,
                'assigned_to_email': recipient_email.lower(),
                'is_assigned': True,
                'is_used': False,
                'qr_code_data': qr_code_data,
                'short_url': short_url
            }

            result = self.create_coupon(coupon_data)
            
            if result:
                current_app.logger.info(f"Gift coupon created: {coupon_code} for {recipient_email}")
                return {
                    'success': True,
                    'coupon': result,
                    'message': f'Gift coupon created successfully for {recipient_email}'
                }
            else:
                raise Exception("Failed to create coupon")

        except Exception as e:
            current_app.logger.error(f"Error creating gift coupon: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create gift coupon'
            }
    
    # Referral coupon creation
    def create_referral_coupon(self, referrer_email: str, referee_email: str,
                              discount_value: float, discount_type: str = 'fixed_amount',
                              referrer_gets_reward: bool = False, 
                              referrer_reward_value: float = None) -> Dict[str, Any]:
        """Create a referral coupon system"""
        try:
            from datetime import timedelta
            
            # Create coupon for referee
            referee_coupon_code = self.generate_coupon_code()
            expiry_date = (datetime.utcnow() + timedelta(days=30)).isoformat()

            referee_coupon = {
                'code': referee_coupon_code,
                'name': f'Referral Discount - {discount_value}{"%" if discount_type == "percentage" else "$"} Off',
                'description': f'Special referral discount from {referrer_email}',
                'discount_type': discount_type,
                'discount_value': discount_value,
                'expiry_date': expiry_date,
                'assigned_to_email': referee_email.lower(),
                'is_assigned': True,
                'is_used': False,
                'qr_code_data': f"https://skinandwicks.com/claim/{referee_coupon_code}",
                'short_url': f"https://swicks.co/{referee_coupon_code[:6]}"
            }

            # Create referee coupon
            referee_result = self.create_coupon(referee_coupon)
            
            referrer_coupon_result = None
            if referrer_gets_reward and referrer_reward_value:
                # Create reward coupon for referrer
                referrer_coupon_code = self.generate_coupon_code()

                referrer_coupon = {
                    'code': referrer_coupon_code,
                    'name': f'Referrer Reward - {referrer_reward_value}{"%" if discount_type == "percentage" else "$"} Off',
                    'description': f'Thank you for referring {referee_email}',
                    'discount_type': discount_type,
                    'discount_value': referrer_reward_value,
                    'expiry_date': expiry_date,
                    'assigned_to_email': referrer_email.lower(),
                    'is_assigned': True,
                    'is_used': False,
                    'qr_code_data': f"https://skinandwicks.com/claim/{referrer_coupon_code}",
                    'short_url': f"https://swicks.co/{referrer_coupon_code[:6]}"
                }

                referrer_coupon_result = self.create_coupon(referrer_coupon)

            # Create referral tracking record
            if referee_result:
                referral_data = {
                    'referrer_email': referrer_email.lower(),
                    'referee_email': referee_email.lower(),
                    'coupon_id': referee_result['id'],
                    'discount_applied': discount_value,
                    'discount_type': discount_type,
                    'referrer_gets_reward': referrer_gets_reward,
                    'referrer_reward_coupon_id': referrer_coupon_result['id'] if referrer_coupon_result else None,
                    'referrer_reward_value': referrer_reward_value,
                    'redeemed_at': datetime.utcnow().isoformat()
                }

                self.create_referral(referral_data)

            return {
                'success': True,
                'referee_coupon': referee_result,
                'referrer_coupon': referrer_coupon_result,
                'message': 'Referral coupons created successfully'
            }

        except Exception as e:
            current_app.logger.error(f"Error creating referral coupon: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create referral coupon'
            }


# Global instance
supabase_service = SupabaseService()