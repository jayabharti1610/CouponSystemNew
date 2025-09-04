# Add these routes to your main app.py file or create as a separate routes file

from flask import render_template, request, jsonify, redirect, url_for, flash
from supabase_service import supabase_service
from datetime import datetime, timedelta
import uuid

# Home page - showing available coupons
@app.route('/')
def index():
    try:
        # Get all active (not used and not expired) coupons
        all_coupons = supabase_service.get_all_coupons()
        
        # Filter active coupons
        active_coupons = []
        current_time = datetime.utcnow()
        
        for coupon in all_coupons:
            if not coupon.get('is_used') and coupon.get('expiry_date'):
                expiry_date = datetime.fromisoformat(coupon['expiry_date'].replace('Z', '+00:00'))
                if expiry_date > current_time:
                    active_coupons.append(coupon)
        
        # Get analytics data
        analytics = supabase_service.get_coupon_analytics()
        
        return render_template('index.html', 
                             coupons=active_coupons, 
                             analytics=analytics)
    except Exception as e:
        app.logger.error(f"Error in index route: {str(e)}")
        return render_template('index.html', coupons=[], analytics={})

# Admin dashboard
@app.route('/admin')
def admin():
    try:
        # Get all coupons for admin view
        coupons = supabase_service.get_all_coupons()
        
        # Get analytics
        analytics = supabase_service.get_coupon_analytics()
        
        # Get recent activity (you can implement this based on your needs)
        recent_activity = []  # Placeholder
        
        return render_template('admin.html', 
                             coupons=coupons, 
                             analytics=analytics,
                             recent_activity=recent_activity)
    except Exception as e:
        app.logger.error(f"Error in admin route: {str(e)}")
        return render_template('admin.html', coupons=[], analytics={}, recent_activity=[])

# Claim coupon page
@app.route('/claim', methods=['GET', 'POST'])
def claim_page():
    if request.method == 'GET':
        return render_template('claim.html')
    
    try:
        coupon_code = request.form.get('coupon_code', '').strip().upper()
        user_email = request.form.get('user_email', '').strip()
        
        if not coupon_code:
            return render_template('claim.html', error="Please enter a coupon code")
        
        # Get coupon from Supabase
        coupon = supabase_service.get_coupon_by_code(coupon_code)
        
        if not coupon:
            return render_template('claim.html', error="Coupon code not found")
        
        # Check if coupon is valid
        if coupon.get('is_used'):
            return render_template('claim.html', error="This coupon has already been used")
        
        # Check expiry date
        if coupon.get('expiry_date'):
            expiry_date = datetime.fromisoformat(coupon['expiry_date'].replace('Z', '+00:00'))
            if expiry_date <= datetime.utcnow():
                return render_template('claim.html', error="This coupon has expired")
        
        # Check if coupon is assigned to specific email
        if coupon.get('is_assigned') and coupon.get('assigned_to_email'):
            if not user_email or user_email.lower() != coupon['assigned_to_email'].lower():
                return render_template('claim.html', 
                                     error="This coupon is assigned to a specific email address")
        
        return render_template('claim.html', coupon=coupon, user_email=user_email)
        
    except Exception as e:
        app.logger.error(f"Error in claim route: {str(e)}")
        return render_template('claim.html', error="An error occurred while processing your request")

# Claim coupon (use coupon)
@app.route('/claim/<coupon_id>', methods=['POST'])
def use_coupon(coupon_id):
    try:
        user_email = request.form.get('user_email', '').strip()
        
        # Get coupon by ID
        all_coupons = supabase_service.get_all_coupons()
        coupon = None
        for c in all_coupons:
            if c['id'] == coupon_id:
                coupon = c
                break
        
        if not coupon:
            return render_template('claim.html', error="Coupon not found")
        
        # Mark coupon as used
        success = supabase_service.mark_coupon_used(coupon['code'])
        
        if success:
            # Update usage tracking
            order_data = {
                'user_email': user_email,
                'discount_amount': float(coupon['discount_value']),
                'used_at': datetime.utcnow().isoformat()
            }
            supabase_service.update_coupon_usage_tracking(coupon['code'], order_data)
            
            return render_template('claim.html', 
                                 success="Coupon claimed successfully!", 
                                 claimed_code=coupon['code'])
        else:
            return render_template('claim.html', error="Failed to claim coupon. Please try again.")
            
    except Exception as e:
        app.logger.error(f"Error using coupon {coupon_id}: {str(e)}")
        return render_template('claim.html', error="An error occurred while claiming the coupon")

# Create new coupon (Admin)
@app.route('/admin/create-coupon', methods=['POST'])
def create_coupon():
    try:
        coupon_data = {
            'code': request.form.get('code', '').strip().upper(),
            'name': request.form.get('name', '').strip(),
            'description': request.form.get('description', '').strip(),
            'discount_type': request.form.get('discount_type'),
            'discount_value': float(request.form.get('discount_value', 0)),
            'minimum_spend': float(request.form.get('minimum_order_value', 0)) if request.form.get('minimum_order_value') else None,
            'expiry_date': request.form.get('expiry_date'),
            'usage_limit': int(request.form.get('usage_limit', 0)) if request.form.get('usage_limit') else None,
            'is_used': False,
            'is_assigned': False
        }
        
        # Validate required fields
        if not coupon_data['code'] or not coupon_data['name'] or not coupon_data['discount_type']:
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('admin'))
        
        # Convert expiry date to proper format
        if coupon_data['expiry_date']:
            expiry_date = datetime.strptime(coupon_data['expiry_date'], '%Y-%m-%d')
            coupon_data['expiry_date'] = expiry_date.isoformat()
        else:
            # Default to 1 year from now
            expiry_date = datetime.utcnow() + timedelta(days=365)
            coupon_data['expiry_date'] = expiry_date.isoformat()
        
        # Create coupon in Supabase
        created_coupon = supabase_service.create_coupon(coupon_data)
        
        if created_coupon:
            flash('Coupon created successfully!', 'success')
        else:
            flash('Failed to create coupon. Code might already exist.', 'error')
        
        return redirect(url_for('admin'))
        
    except Exception as e:
        app.logger.error(f"Error creating coupon: {str(e)}")
        flash('An error occurred while creating the coupon', 'error')
        return redirect(url_for('admin'))

# Update coupon status
@app.route('/admin/coupon/<coupon_id>/status', methods=['PATCH'])
def update_coupon_status(coupon_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['active', 'inactive']:
            return jsonify({'error': 'Invalid status'}), 400
        
        # Update coupon (you might need to implement status field in your schema)
        updates = {'updated_at': datetime.utcnow().isoformat()}
        if new_status == 'inactive':
            updates['is_used'] = True  # Mark as used to make it inactive
        else:
            updates['is_used'] = False
        
        updated_coupon = supabase_service.update_coupon(coupon_id, updates)
        
        if updated_coupon:
            return jsonify({'message': f'Coupon {new_status}', 'coupon': updated_coupon})
        else:
            return jsonify({'error': 'Failed to update coupon'}), 500
            
    except Exception as e:
        app.logger.error(f"Error updating coupon status: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

# Delete coupon
@app.route('/admin/coupon/<coupon_id>', methods=['DELETE'])
def delete_coupon(coupon_id):
    try:
        success = supabase_service.delete_coupon(coupon_id)
        
        if success:
            return jsonify({'message': 'Coupon deleted successfully'})
        else:
            return jsonify({'error': 'Failed to delete coupon'}), 500
            
    except Exception as e:
        app.logger.error(f"Error deleting coupon: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

# Get coupon by ID (API)
@app.route('/api/coupons/<coupon_id>')
def get_coupon_api(coupon_id):
    try:
        all_coupons = supabase_service.get_all_coupons()
        coupon = None
        for c in all_coupons:
            if c['id'] == coupon_id:
                coupon = c
                break
        
        if coupon:
            return jsonify(coupon)
        else:
            return jsonify({'error': 'Coupon not found'}), 404
            
    except Exception as e:
        app.logger.error(f"Error fetching coupon {coupon_id}: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

# Get analytics (API)
@app.route('/api/stats')
def get_stats():
    try:
        analytics = supabase_service.get_coupon_analytics()
        return jsonify(analytics)
    except Exception as e:
        app.logger.error(f"Error fetching stats: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

# Shopify integration routes
@app.route('/shopify')
def shopify_integration():
    try:
        # Get Shopify configuration (assuming store name from config)
        store_name = app.config.get('SHOPIFY_STORE_NAME', 'default')
        shopify_config = supabase_service.get_shopify_config(store_name)
        
        shopify_connected = shopify_config and shopify_config.get('is_connected', False)
        store_name_display = shopify_config.get('store_name') if shopify_config else None
        
        # Get Shopify coupons (placeholder - you'd implement Shopify API calls)
        shopify_coupons = []
        
        return render_template('shopify.html',
                             shopify_connected=shopify_connected,
                             store_name=store_name_display,
                             shopify_coupons=shopify_coupons)
    except Exception as e:
        app.logger.error(f"Error in shopify route: {str(e)}")
        return render_template('shopify.html', shopify_connected=False, shopify_coupons=[])

@app.route('/shopify/connect', methods=['POST'])
def shopify_connect():
    try:
        config_data = {
            'store_name': request.form.get('shop_url'),
            'api_key': request.form.get('api_key'),
            'api_secret': request.form.get('api_secret'),
            'access_token': request.form.get('api_secret'),  # Simplified for demo
            'is_connected': True
        }
        
        saved_config = supabase_service.save_shopify_config(config_data)
        
        if saved_config:
            flash('Shopify store connected successfully!', 'success')
        else:
            flash('Failed to connect Shopify store', 'error')
        
        return redirect(url_for('shopify_integration'))
        
    except Exception as e:
        app.logger.error(f"Error connecting Shopify: {str(e)}")
        flash('An error occurred while connecting to Shopify', 'error')
        return redirect(url_for('shopify_integration'))

@app.route('/shopify/sync', methods=['POST'])
def shopify_sync():
    try:
        # Placeholder for Shopify sync logic
        # You would implement actual Shopify API calls here
        
        return jsonify({
            'success': True,
            'message': 'Shopify data synced successfully'
        })
        
    except Exception as e:
        app.logger.error(f"Error syncing Shopify: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to sync Shopify data'
        }), 500

# Referral system routes
@app.route('/referral/create', methods=['POST'])
def create_referral():
    try:
        referral_data = {
            'referrer_email': request.form.get('referrer_email'),
            'referee_email': request.form.get('referee_email'),
            'coupon_id': request.form.get('coupon_id'),
            'discount_applied': float(request.form.get('discount_applied', 0)),
            'discount_type': request.form.get('discount_type', 'fixed'),
            'referrer_gets_reward': request.form.get('referrer_gets_reward') == 'true',
            'referrer_reward_value': float(request.form.get('referrer_reward_value', 0)) if request.form.get('referrer_reward_value') else None,
            'notes': request.form.get('notes', '')
        }
        
        created_referral = supabase_service.create_referral(referral_data)
        
        if created_referral:
            return jsonify({
                'success': True,
                'message': 'Referral created successfully',
                'referral': created_referral
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to create referral'
            }), 500
            
    except Exception as e:
        app.logger.error(f"Error creating referral: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while creating referral'
        }), 500

# Get user's coupons
@app.route('/api/user/<email>/coupons')
def get_user_coupons(email):
    try:
        coupons = supabase_service.get_coupons_by_email(email)
        return jsonify(coupons)
    except Exception as e:
        app.logger.error(f"Error fetching user coupons for {email}: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

# Generate coupon for user
@app.route('/api/user/<email>/generate-coupon', methods=['POST'])
def generate_user_coupon(email):
    try:
        data = request.get_json()
        
        expiry_date = datetime.utcnow() + timedelta(days=data.get('expiry_days', 30))
        
        coupon_id = supabase_service.generate_user_coupon(
            email=email,
            name=data.get('name', 'Personal Coupon'),
            description=data.get('description', 'Personal discount coupon'),
            discount_value=float(data.get('discount_value', 10)),
            discount_type=data.get('discount_type', 'fixed_amount'),
            expiry_date=expiry_date,
            minimum_spend=float(data.get('minimum_spend', 0)) if data.get('minimum_spend') else None
        )
        
        if coupon_id:
            # Get the created coupon
            coupon = supabase_service.get_coupon_by_code(f"GENERATED_{coupon_id}")  # Adjust based on your generation logic
            return jsonify({
                'success': True,
                'message': 'Coupon generated successfully',
                'coupon_id': coupon_id,
                'coupon': coupon
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to generate coupon'
            }), 500
            
    except Exception as e:
        app.logger.error(f"Error generating coupon for {email}: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while generating coupon'
        }), 500

# Bulk operations
@app.route('/api/coupons/bulk-delete', methods=['POST'])
def bulk_delete_coupons():
    try:
        data = request.get_json()
        coupon_ids = data.get('couponIds', [])
        
        deleted_count = 0
        for coupon_id in coupon_ids:
            if supabase_service.delete_coupon(coupon_id):
                deleted_count += 1
        
        return jsonify({
            'success': True,
            'message': f'{deleted_count} coupons deleted successfully'
        })
        
    except Exception as e:
        app.logger.error(f"Error bulk deleting coupons: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred during bulk delete'
        }), 500

@app.route('/api/coupons/bulk-status', methods=['POST'])
def bulk_update_status():
    try:
        data = request.get_json()
        coupon_ids = data.get('couponIds', [])
        status = data.get('status')
        
        updated_count = 0
        updates = {'is_used': status == 'inactive'}
        
        for coupon_id in coupon_ids:
            if supabase_service.update_coupon(coupon_id, updates):
                updated_count += 1
        
        return jsonify({
            'success': True,
            'message': f'{updated_count} coupons updated successfully'
        })
        
    except Exception as e:
        app.logger.error(f"Error bulk updating coupon status: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred during bulk update'
        }), 500