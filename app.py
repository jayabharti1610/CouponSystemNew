# app.py - Updated for your Supabase Database Schema
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
import os
import json
from datetime import datetime, timedelta
import uuid
import secrets
import string
import requests
from supabase import create_client, Client
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
CORS(app)

# UPDATE THESE WITH YOUR SUPABASE CREDENTIALS
SUPABASE_URL = "https://xynqidcehmexicyrnuql.supabase.co"  # Replace with your Supabase URL
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh5bnFpZGNlaG1leGljeXJudXFsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY3NTYzMzgsImV4cCI6MjA3MjMzMjMzOH0.avR3DF90Z-_mpMEl1-D8PzhCfDz4buor7BwmwDToatA"  # Replace with your Supabase anon key

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class CouponManager:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    def generate_coupon_code(self, length: int = 8) -> str:
        """Generate a random coupon code"""
        characters = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))

    def create_gift_coupon(self, recipient_email: str, sender_email: str, 
                          name: str, discount_type: str, discount_value: float,
                          expiry_date: str, description: str = None, 
                          minimum_spend: float = None) -> Dict[str, Any]:
        """Create a gift coupon"""
        try:
            coupon_code = self.generate_coupon_code()
            
            # Generate QR code data (placeholder URL for now)
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
                'assigned_to_email': recipient_email,
                'is_assigned': True,
                'is_used': False,
                'qr_code_data': qr_code_data,
                'short_url': short_url,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }

            result = self.supabase.table('coupons').insert(coupon_data).execute()
            
            if result.data:
                logger.info(f"Gift coupon created: {coupon_code} for {recipient_email}")
                return {
                    'success': True,
                    'coupon': result.data[0],
                    'message': f'Gift coupon created successfully for {recipient_email}'
                }
            else:
                raise Exception("Failed to create coupon")

        except Exception as e:
            logger.error(f"Error creating gift coupon: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create gift coupon'
            }

    def create_referral_coupon(self, referrer_email: str, referee_email: str,
                              discount_value: float, discount_type: str = 'fixed_amount',
                              referrer_gets_reward: bool = False, 
                              referrer_reward_value: float = None) -> Dict[str, Any]:
        """Create a referral coupon system"""
        try:
            # Create coupon for referee
            referee_coupon_code = self.generate_coupon_code()
            expiry_date = (datetime.now() + timedelta(days=30)).isoformat()

            referee_coupon = {
                'code': referee_coupon_code,
                'name': f'Referral Discount - {discount_value}{"%" if discount_type == "percentage" else "$"} Off',
                'description': f'Special referral discount from {referrer_email}',
                'discount_type': discount_type,
                'discount_value': discount_value,
                'expiry_date': expiry_date,
                'assigned_to_email': referee_email,
                'is_assigned': True,
                'is_used': False,
                'qr_code_data': f"https://skinandwicks.com/claim/{referee_coupon_code}",
                'short_url': f"https://swicks.co/{referee_coupon_code[:6]}",
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }

            # Insert referee coupon
            referee_result = self.supabase.table('coupons').insert(referee_coupon).execute()
            
            referrer_coupon_id = None
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
                    'assigned_to_email': referrer_email,
                    'is_assigned': True,
                    'is_used': False,
                    'qr_code_data': f"https://skinandwicks.com/claim/{referrer_coupon_code}",
                    'short_url': f"https://swicks.co/{referrer_coupon_code[:6]}",
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }

                referrer_result = self.supabase.table('coupons').insert(referrer_coupon).execute()
                referrer_coupon_id = referrer_result.data[0]['id'] if referrer_result.data else None

            # Create referral tracking record
            referral_data = {
                'referrer_email': referrer_email,
                'referee_email': referee_email,
                'coupon_id': referee_result.data[0]['id'] if referee_result.data else None,
                'discount_applied': discount_value,
                'discount_type': discount_type,
                'referrer_gets_reward': referrer_gets_reward,
                'referrer_reward_coupon_id': referrer_coupon_id,
                'referrer_reward_value': referrer_reward_value,
                'redeemed_at': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }

            self.supabase.table('referrals').insert(referral_data).execute()

            return {
                'success': True,
                'referee_coupon': referee_result.data[0] if referee_result.data else None,
                'referrer_coupon_id': referrer_coupon_id,
                'message': 'Referral coupons created successfully'
            }

        except Exception as e:
            logger.error(f"Error creating referral coupon: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create referral coupon'
            }

    def get_coupons_by_email(self, email: str) -> List[Dict[str, Any]]:
        """Get all coupons assigned to an email"""
        try:
            result = self.supabase.table('coupons').select('*').eq('assigned_to_email', email).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error fetching coupons for {email}: {str(e)}")
            return []

    def get_all_coupons(self) -> List[Dict[str, Any]]:
        """Get all coupons"""
        try:
            result = self.supabase.table('coupons').select('*').order('created_at', desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error fetching all coupons: {str(e)}")
            return []

    def get_analytics(self) -> Dict[str, Any]:
        """Get coupon analytics"""
        try:
            # Get all coupons
            coupons_result = self.supabase.table('coupons').select('*').execute()
            coupons = coupons_result.data if coupons_result.data else []

            # Get referrals to identify referral coupons
            referrals_result = self.supabase.table('referrals').select('coupon_id').execute()
            referral_coupon_ids = set(r['coupon_id'] for r in (referrals_result.data or []) if r['coupon_id'])

            now = datetime.now()
            
            total_coupons = len(coupons)
            redeemed_coupons = len([c for c in coupons if c['is_used']])
            
            # Calculate expired coupons (handle both timestamp formats)
            expired_coupons = 0
            active_coupons = 0
            for c in coupons:
                if c['is_used']:
                    continue
                try:
                    # Handle different timestamp formats
                    expiry_str = c['expiry_date']
                    if expiry_str.endswith('Z'):
                        expiry_date = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
                    else:
                        expiry_date = datetime.fromisoformat(expiry_str)
                    
                    if expiry_date < now:
                        expired_coupons += 1
                    else:
                        active_coupons += 1
                except:
                    # If date parsing fails, consider it active
                    active_coupons += 1

            # Calculate total value of active coupons
            total_value = 0
            for c in coupons:
                if c['is_used']:
                    continue
                try:
                    expiry_str = c['expiry_date']
                    if expiry_str.endswith('Z'):
                        expiry_date = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
                    else:
                        expiry_date = datetime.fromisoformat(expiry_str)
                    
                    if expiry_date >= now:
                        total_value += float(c['discount_value'])
                except:
                    total_value += float(c['discount_value'])

            # Separate gift vs referral coupons
            gift_coupons = [c for c in coupons if c['id'] not in referral_coupon_ids]
            referral_coupons = [c for c in coupons if c['id'] in referral_coupon_ids]

            gift_redeemed = len([c for c in gift_coupons if c['is_used']])
            referral_redeemed = len([c for c in referral_coupons if c['is_used']])

            gift_redemption_rate = (gift_redeemed / len(gift_coupons) * 100) if gift_coupons else 0
            referral_redemption_rate = (referral_redeemed / len(referral_coupons) * 100) if referral_coupons else 0
            overall_redemption_rate = (redeemed_coupons / total_coupons * 100) if total_coupons else 0

            return {
                'total_coupons': total_coupons,
                'redeemed_coupons': redeemed_coupons,
                'expired_coupons': expired_coupons,
                'active_coupons': active_coupons,
                'total_value': total_value,
                'gift_coupons': len(gift_coupons),
                'referral_coupons': len(referral_coupons),
                'gift_redemption_rate': gift_redemption_rate,
                'referral_redemption_rate': referral_redemption_rate,
                'overall_redemption_rate': overall_redemption_rate
            }

        except Exception as e:
            logger.error(f"Error fetching analytics: {str(e)}")
            return {
                'total_coupons': 0,
                'redeemed_coupons': 0,
                'expired_coupons': 0,
                'active_coupons': 0,
                'total_value': 0,
                'gift_coupons': 0,
                'referral_coupons': 0,
                'gift_redemption_rate': 0,
                'referral_redemption_rate': 0,
                'overall_redemption_rate': 0
            }

    def mark_coupon_used(self, coupon_code: str) -> Dict[str, Any]:
        """Mark a coupon as used"""
        try:
            result = self.supabase.table('coupons').update({
                'is_used': True,
                'used_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }).eq('code', coupon_code).execute()

            if result.data:
                return {'success': True, 'message': 'Coupon marked as used'}
            else:
                return {'success': False, 'message': 'Coupon not found'}

        except Exception as e:
            logger.error(f"Error marking coupon as used: {str(e)}")
            return {'success': False, 'error': str(e)}


# Initialize coupon manager
coupon_manager = CouponManager(supabase)

# Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/admin')
def admin():
    """Admin dashboard page"""
    analytics = coupon_manager.get_analytics()
    coupons = coupon_manager.get_all_coupons()
    return render_template('admin.html', analytics=analytics, coupons=coupons)

@app.route('/shopify')
def shopify_integration():
    """Shopify integration page"""
    return render_template('shopify.html')

@app.route('/claim')
def claim_page():
    """Coupon claim page"""
    return render_template('claim.html')

@app.route('/claim/<coupon_code>')
def claim_with_code(coupon_code):
    """Direct coupon claim with code"""
    return render_template('claim.html', coupon_code=coupon_code)

# API Routes
@app.route('/api/coupons', methods=['GET'])
def get_coupons():
    """Get all coupons or filter by email"""
    email = request.args.get('email')
    
    if email:
        coupons = coupon_manager.get_coupons_by_email(email)
    else:
        coupons = coupon_manager.get_all_coupons()
    
    return jsonify({'success': True, 'data': coupons})

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get coupon analytics"""
    analytics = coupon_manager.get_analytics()
    return jsonify({'success': True, 'data': analytics})

@app.route('/api/coupons/gift', methods=['POST'])
def create_gift_coupon():
    """Create a gift coupon"""
    try:
        data = request.get_json()
        
        required_fields = ['recipient_email', 'sender_email', 'name', 'discount_type', 
                          'discount_value', 'expiry_date']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400

        result = coupon_manager.create_gift_coupon(
            recipient_email=data['recipient_email'],
            sender_email=data['sender_email'],
            name=data['name'],
            discount_type=data['discount_type'],
            discount_value=float(data['discount_value']),
            expiry_date=data['expiry_date'],
            description=data.get('description'),
            minimum_spend=float(data['minimum_spend']) if data.get('minimum_spend') else None
        )

        return jsonify(result), 201 if result['success'] else 400

    except Exception as e:
        logger.error(f"Error in create_gift_coupon API: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/coupons/referral', methods=['POST'])
def create_referral_coupon():
    """Create a referral coupon"""
    try:
        data = request.get_json()
        
        required_fields = ['referrer_email', 'referee_email', 'discount_value', 'discount_type']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400

        result = coupon_manager.create_referral_coupon(
            referrer_email=data['referrer_email'],
            referee_email=data['referee_email'],
            discount_value=float(data['discount_value']),
            discount_type=data['discount_type'],
            referrer_gets_reward=data.get('referrer_gets_reward', False),
            referrer_reward_value=float(data['referrer_reward_value']) if data.get('referrer_reward_value') else None
        )

        return jsonify(result), 201 if result['success'] else 400

    except Exception as e:
        logger.error(f"Error in create_referral_coupon API: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
@app.route('/admin/create-coupon', methods=['POST'])
def create_coupon():
    try:
        # Get form data
        code = request.form.get('code')
        name = request.form.get('name', code)  # Use code as name if name not provided
        description = request.form.get('description')
        discount_type = request.form.get('discount_type')
        discount_value = float(request.form.get('discount_value'))
        expiry_date = request.form.get('expiry_date')
        minimum_spend = request.form.get('minimum_spend')
        
        # Validate required fields
        if not code or not discount_type or not discount_value:
            flash('Code, discount type, and discount value are required!', 'error')
            return redirect(url_for('admin'))
        
        # Process optional fields
        minimum_spend = float(minimum_spend) if minimum_spend else None
        
        # Handle expiry date
        if expiry_date:
            expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').isoformat()
        else:
            # Default to 1 year from now if not specified
            expiry_date = (datetime.now() + timedelta(days=365)).isoformat()
        
        # Check if coupon code already exists
        existing_coupon = supabase.table('coupons').select('*').eq('code', code).execute()
        if existing_coupon.data:
            flash(f'Coupon code "{code}" already exists!', 'error')
            return redirect(url_for('admin'))
        
        # Create coupon data
        coupon_data = {
            'code': code.upper(),
            'name': name,
            'description': description,
            'discount_type': discount_type,
            'discount_value': discount_value,
            'minimum_spend': minimum_spend,
            'expiry_date': expiry_date,
            'is_used': False,
            'is_assigned': False,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Insert into database
        result = supabase.table('coupons').insert(coupon_data).execute()
        
        if result.data:
            flash(f'Coupon "{code}" created successfully!', 'success')
        else:
            flash('Failed to create coupon. Please try again.', 'error')
            
    except ValueError as e:
        flash('Invalid input values. Please check your entries.', 'error')
    except Exception as e:
        print(f"Error creating coupon: {e}")
        flash('An error occurred while creating the coupon.', 'error')
    
    return redirect(url_for('admin'))

@app.route('/api/coupons/claim', methods=['POST'])
def claim_coupon():
    """Claim a coupon"""
    try:
        data = request.get_json()
        email = data.get('email')
        coupon_code = data.get('coupon_code')

        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400

        if coupon_code:
            # Check if specific coupon exists and is valid
            result = supabase.table('coupons').select('*').eq('code', coupon_code).execute()
            
            if not result.data:
                return jsonify({'success': False, 'message': 'Invalid coupon code'}), 404
            
            coupon = result.data[0]
            
            if coupon['is_used']:
                return jsonify({'success': False, 'message': 'Coupon has already been used'}), 400
            
            # Check expiry date
            try:
                expiry_str = coupon['expiry_date']
                if expiry_str.endswith('Z'):
                    expiry_date = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
                else:
                    expiry_date = datetime.fromisoformat(expiry_str)
                
                if expiry_date < datetime.now():
                    return jsonify({'success': False, 'message': 'Coupon has expired'}), 400
            except:
                pass  # If date parsing fails, assume it's valid
            
            # Update coupon to assign to claiming email if not already assigned
            if not coupon['assigned_to_email']:
                supabase.table('coupons').update({
                    'assigned_to_email': email,
                    'is_assigned': True,
                    'updated_at': datetime.now().isoformat()
                }).eq('code', coupon_code).execute()

        # Return all coupons for this email
        user_coupons = coupon_manager.get_coupons_by_email(email)
        
        return jsonify({
            'success': True,
            'message': f'Found {len(user_coupons)} coupons for {email}',
            'coupons': user_coupons
        })

    except Exception as e:
        logger.error(f"Error in claim_coupon API: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/coupons/<coupon_id>/use', methods=['POST'])
def use_coupon(coupon_id):
    """Mark a coupon as used"""
    try:
        result = supabase.table('coupons').select('*').eq('id', coupon_id).execute()
        
        if not result.data:
            return jsonify({'success': False, 'message': 'Coupon not found'}), 404
        
        coupon = result.data[0]
        
        if coupon['is_used']:
            return jsonify({'success': False, 'message': 'Coupon already used'}), 400
        
        # Mark as used
        mark_result = coupon_manager.mark_coupon_used(coupon['code'])
        return jsonify(mark_result)

    except Exception as e:
        logger.error(f"Error using coupon: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/shopify/sync', methods=['POST'])
def sync_shopify_orders():
    """Sync orders from Shopify (demo functionality)"""
    try:
        # This would contain actual Shopify API integration
        # For now, return mock data
        mock_stats = {
            'total_orders': 150,
            'orders_with_coupons': 45,
            'unique_coupons': 38,
            'total_discount': 892.50,
            'synced_orders': 150
        }
        
        return jsonify({
            'success': True,
            'message': 'Shopify orders synced successfully (demo)',
            'stats': mock_stats
        })

    except Exception as e:
        logger.error(f"Error syncing Shopify orders: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Additional admin routes from the additional_admin_routes.py file
@app.route('/api/coupons/<coupon_id>')
def get_coupon_api(coupon_id):
    """API endpoint to get coupon data for editing"""
    try:
        result = supabase.table('coupons').select('*').eq('id', coupon_id).execute()
        if result.data:
            return jsonify(result.data[0])
        else:
            return jsonify({'error': 'Coupon not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/toggle-coupon-status', methods=['POST'])
def toggle_coupon_status():
    """Toggle coupon active/inactive status"""
    try:
        coupon_id = request.json.get('coupon_id')
        new_status = request.json.get('status')
        
        if not coupon_id or not new_status:
            return jsonify({'success': False, 'error': 'Missing parameters'})
        
        # Update coupon status (using is_used as status indicator)
        is_used = new_status == 'inactive'
        result = supabase.table('coupons').update({
            'is_used': is_used,
            'updated_at': datetime.now().isoformat()
        }).eq('id', coupon_id).execute()
        
        if result.data:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to update status'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/delete-coupon', methods=['POST'])
def delete_coupon():
    """Delete a coupon"""
    try:
        coupon_id = request.json.get('coupon_id')
        
        if not coupon_id:
            return jsonify({'success': False, 'error': 'Missing coupon ID'})
        
        # Get coupon info for logging
        coupon_result = supabase.table('coupons').select('code').eq('id', coupon_id).execute()
        coupon_code = coupon_result.data[0]['code'] if coupon_result.data else 'Unknown'
        
        # Delete coupon
        result = supabase.table('coupons').delete().eq('id', coupon_id).execute()
        
        if result.data:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to delete coupon'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/bulk-delete', methods=['POST'])
def bulk_delete_coupons():
    """Delete multiple coupons"""
    try:
        coupon_ids = request.json.get('coupon_ids', [])
        
        if not coupon_ids:
            return jsonify({'success': False, 'error': 'No coupons selected'})
        
        # Delete coupons
        deleted_count = 0
        for coupon_id in coupon_ids:
            result = supabase.table('coupons').delete().eq('id', coupon_id).execute()
            if result.data:
                deleted_count += 1
        
        if deleted_count > 0:
            return jsonify({'success': True, 'deleted_count': deleted_count})
        else:
            return jsonify({'success': False, 'error': 'No coupons were deleted'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/bulk-update-status', methods=['POST'])
def bulk_update_status():
    """Update status for multiple coupons"""
    try:
        coupon_ids = request.json.get('coupon_ids', [])
        new_status = request.json.get('status')
        
        if not coupon_ids or not new_status:
            return jsonify({'success': False, 'error': 'Missing parameters'})
        
        # Update coupons
        updated_count = 0
        is_used = new_status == 'inactive'
        for coupon_id in coupon_ids:
            result = supabase.table('coupons').update({
                'is_used': is_used,
                'updated_at': datetime.now().isoformat()
            }).eq('id', coupon_id).execute()
            if result.data:
                updated_count += 1
        
        if updated_count > 0:
            return jsonify({'success': True, 'updated_count': updated_count})
        else:
            return jsonify({'success': False, 'error': 'No coupons were updated'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)