from flask import request, redirect, url_for, flash
from datetime import datetime

@app.route('/admin/create-coupon', methods=['POST'])
def create_coupon():
    try:
        # Get form data
        code = request.form.get('code')
        description = request.form.get('description')
        discount_type = request.form.get('discount_type')
        discount_value = float(request.form.get('discount_value'))
        usage_limit = request.form.get('usage_limit')
        expiry_date = request.form.get('expiry_date')
        minimum_order_value = request.form.get('minimum_order_value')
        
        # Validate required fields
        if not code or not discount_type or not discount_value:
            flash('Code, discount type, and discount value are required!', 'error')
            return redirect(url_for('admin'))
        
        # Process optional fields
        usage_limit = int(usage_limit) if usage_limit else None
        minimum_order_value = float(minimum_order_value) if minimum_order_value else 0.0
        expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date() if expiry_date else None
        
        # Check if coupon code already exists
        existing_coupon = supabase.table('coupons').select('*').eq('code', code).execute()
        if existing_coupon.data:
            flash(f'Coupon code "{code}" already exists!', 'error')
            return redirect(url_for('admin'))
        
        # Create coupon data
        coupon_data = {
            'code': code.upper(),  # Store codes in uppercase for consistency
            'description': description,
            'discount_type': discount_type,
            'discount_value': discount_value,
            'usage_limit': usage_limit,
            'usage_count': 0,
            'expiry_date': expiry_date.isoformat() if expiry_date else None,
            'minimum_order_value': minimum_order_value,
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Insert into database
        result = supabase.table('coupons').insert(coupon_data).execute()
        
        if result.data:
            flash(f'Coupon "{code}" created successfully!', 'success')
            
            # Log activity
            activity_data = {
                'type': 'create',
                'message': f'Created coupon "{code}" with {discount_value}{"%" if discount_type == "percentage" else "$"} discount',
                'timestamp': datetime.now().isoformat(),
                'icon': '➕'
            }
            supabase.table('activity_log').insert(activity_data).execute()
            
        else:
            flash('Failed to create coupon. Please try again.', 'error')
            
    except ValueError as e:
        flash('Invalid input values. Please check your entries.', 'error')
    except Exception as e:
        print(f"Error creating coupon: {e}")
        flash('An error occurred while creating the coupon.', 'error')
    
    return redirect(url_for('admin'))

# Also add a route for bulk import if you want that functionality
@app.route('/admin/bulk-import', methods=['POST'])
def bulk_import_coupons():
    try:
        if 'file' not in request.files:
            flash('No file selected!', 'error')
            return redirect(url_for('admin'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected!', 'error')
            return redirect(url_for('admin'))
        
        if not file.filename.endswith('.csv'):
            flash('Please upload a CSV file!', 'error')
            return redirect(url_for('admin'))
        
        # Read CSV file
        import csv
        import io
        
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        success_count = 0
        error_count = 0
        
        for row in csv_reader:
            try:
                # Check if required fields are present
                if not all(key in row for key in ['code', 'discount_type', 'discount_value']):
                    error_count += 1
                    continue
                
                # Check if coupon already exists
                existing = supabase.table('coupons').select('*').eq('code', row['code'].upper()).execute()
                if existing.data:
                    error_count += 1
                    continue
                
                # Prepare coupon data
                coupon_data = {
                    'code': row['code'].upper(),
                    'description': row.get('description', ''),
                    'discount_type': row['discount_type'],
                    'discount_value': float(row['discount_value']),
                    'usage_limit': int(row['usage_limit']) if row.get('usage_limit') else None,
                    'usage_count': 0,
                    'expiry_date': datetime.strptime(row['expiry_date'], '%Y-%m-%d').date().isoformat() if row.get('expiry_date') else None,
                    'minimum_order_value': float(row.get('minimum_order_value', 0)),
                    'status': 'active',
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                # Insert coupon
                result = supabase.table('coupons').insert(coupon_data).execute()
                if result.data:
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                print(f"Error importing row {row}: {e}")
                error_count += 1
        
        if success_count > 0:
            flash(f'Successfully imported {success_count} coupons!', 'success')
            
            # Log activity
            activity_data = {
                'type': 'import',
                'message': f'Bulk imported {success_count} coupons from CSV',
                'timestamp': datetime.now().isoformat(),
                'icon': '📥'
            }
            supabase.table('activity_log').insert(activity_data).execute()
        
        if error_count > 0:
            flash(f'{error_count} coupons failed to import (duplicates or invalid data)', 'warning')
            
    except Exception as e:
        print(f"Error in bulk import: {e}")
        flash('Error processing CSV file!', 'error')
    
    return redirect(url_for('admin'))

# Add route for generating reports
@app.route('/admin/generate-report')
def generate_report():
    try:
        # Get all coupons with their usage data
        coupons = supabase.table('coupons').select('*').execute()
        
        # Create a simple CSV report
        import csv
        import io
        from flask import Response
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Code', 'Description', 'Type', 'Value', 'Usage Count', 
            'Usage Limit', 'Status', 'Expiry Date', 'Created Date'
        ])
        
        # Write coupon data
        for coupon in coupons.data:
            writer.writerow([
                coupon['code'],
                coupon.get('description', ''),
                coupon['discount_type'],
                coupon['discount_value'],
                coupon.get('usage_count', 0),
                coupon.get('usage_limit', 'Unlimited'),
                coupon['status'],
                coupon.get('expiry_date', 'No expiry'),
                coupon.get('created_at', '')
            ])
        
        output.seek(0)
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=coupon_report_{datetime.now().strftime("%Y%m%d")}.csv'}
        )
        
    except Exception as e:
        print(f"Error generating report: {e}")
        flash('Error generating report!', 'error')
        return redirect(url_for('admin'))