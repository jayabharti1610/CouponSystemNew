# Add these routes to support the admin functionality

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
        
        # Update coupon status
        result = supabase.table('coupons').update({
            'status': new_status,
            'updated_at': datetime.now().isoformat()
        }).eq('id', coupon_id).execute()
        
        if result.data:
            # Log activity
            activity_data = {
                'type': 'update',
                'message': f'Changed coupon status to {new_status}',
                'timestamp': datetime.now().isoformat(),
                'icon': '🔄'
            }
            supabase.table('activity_log').insert(activity_data).execute()
            
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
            # Log activity
            activity_data = {
                'type': 'delete',
                'message': f'Deleted coupon "{coupon_code}"',
                'timestamp': datetime.now().isoformat(),
                'icon': '🗑️'
            }
            supabase.table('activity_log').insert(activity_data).execute()
            
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
            # Log activity
            activity_data = {
                'type': 'bulk_delete',
                'message': f'Bulk deleted {deleted_count} coupons',
                'timestamp': datetime.now().isoformat(),
                'icon': '🗑️'
            }
            supabase.table('activity_log').insert(activity_data).execute()
            
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
        for coupon_id in coupon_ids:
            result = supabase.table('coupons').update({
                'status': new_status,
                'updated_at': datetime.now().isoformat()
            }).eq('id', coupon_id).execute()
            if result.data:
                updated_count += 1
        
        if updated_count > 0:
            # Log activity
            activity_data = {
                'type': 'bulk_update',
                'message': f'Bulk updated {updated_count} coupons to {new_status}',
                'timestamp': datetime.now().isoformat(),
                'icon': '🔄'
            }
            supabase.table('activity_log').insert(activity_data).execute()
            
            return jsonify({'success': True, 'updated_count': updated_count})
        else:
            return jsonify({'success': False, 'error': 'No coupons were updated'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Also make sure you have the jsonify import at the top of your file
from flask import jsonify