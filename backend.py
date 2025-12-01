# ============================================
# EV CHARGING INFRASTRUCTURE - PYTHON BACKEND
# Flask API Server with ML Models
# ============================================

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime, timedelta
import random

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# ============================================
# DATABASE (In-Memory for Demo)
# ============================================

BACKEND_DATA = {
    'totalEVs': 2037830,
    'totalStations': 29277,
    'coverage': 72.3,
    'co2Saved': 1.2,
    'targetEVs': 10000000,
    'targetYear': 2030
}

STATES = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar',
    'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh',
    'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra',
    'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha',
    'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana',
    'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal'
]

CHARGING_STATIONS = [
    {
        'id': i,
        'name': f'Charging Hub {i}',
        'latitude': 20.5937 + random.uniform(-5, 5),
        'longitude': 78.9629 + random.uniform(-5, 5),
        'state': random.choice(STATES),
        'type': random.choice(['DC Fast', 'AC Level 2', 'AC Level 1']),
        'rating': round(random.uniform(3.5, 5.0), 1),
        'available': random.choice([True, False])
    }
    for i in range(29277)
]

# ============================================
# ROUTES - STATISTICS
# ============================================

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get platform statistics"""
    return jsonify({
        'status': 'success',
        'data': BACKEND_DATA,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/statistics/update', methods=['POST'])
def update_statistics():
    """Update statistics"""
    data = request.json
    BACKEND_DATA.update(data)
    return jsonify({
        'status': 'success',
        'message': 'Statistics updated',
        'data': BACKEND_DATA
    })

# ============================================
# ROUTES - CHARGING STATIONS
# ============================================

@app.route('/api/stations', methods=['GET'])
def get_all_stations():
    """Get all charging stations"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    
    start = (page - 1) * limit
    end = start + limit
    
    return jsonify({
        'status': 'success',
        'data': CHARGING_STATIONS[start:end],
        'total': len(CHARGING_STATIONS),
        'page': page,
        'pages': (len(CHARGING_STATIONS) + limit - 1) // limit
    })

@app.route('/api/stations/search', methods=['POST'])
def search_stations():
    """Search charging stations"""
    data = request.json
    query = data.get('query', '').lower()
    state = data.get('state')
    charger_type = data.get('type')
    
    results = CHARGING_STATIONS
    
    if state:
        results = [s for s in results if s['state'].lower() == state.lower()]
    
    if charger_type:
        results = [s for s in results if s['type'].lower() == charger_type.lower()]
    
    if query:
        results = [s for s in results if query in s['name'].lower()]
    
    return jsonify({
        'status': 'success',
        'data': results[:20],
        'total': len(results)
    })

@app.route('/api/stations/<int:station_id>', methods=['GET'])
def get_station(station_id):
    """Get specific station details"""
    station = next((s for s in CHARGING_STATIONS if s['id'] == station_id), None)
    
    if not station:
        return jsonify({'status': 'error', 'message': 'Station not found'}), 404
    
    return jsonify({
        'status': 'success',
        'data': station
    })

# ============================================
# ROUTES - ANALYTICS
# ============================================

@app.route('/api/analytics/state-distribution', methods=['GET'])
def state_distribution():
    """Get EV distribution by state"""
    state_data = {}
    
    for station in CHARGING_STATIONS:
        state = station['state']
        state_data[state] = state_data.get(state, 0) + 1
    
    return jsonify({
        'status': 'success',
        'data': state_data
    })

@app.route('/api/analytics/charger-types', methods=['GET'])
def charger_types():
    """Get distribution of charger types"""
    type_data = {}
    
    for station in CHARGING_STATIONS:
        ctype = station['type']
        type_data[ctype] = type_data.get(ctype, 0) + 1
    
    return jsonify({
        'status': 'success',
        'data': type_data
    })

@app.route('/api/analytics/growth-trend', methods=['GET'])
def growth_trend():
    """Get historical growth trend"""
    trend = []
    
    for i in range(12):
        date = (datetime.now() - timedelta(days=30*i)).isoformat()
        value = BACKEND_DATA['totalStations'] - (i * 500)
        trend.append({'date': date, 'stations': max(value, 15000)})
    
    return jsonify({
        'status': 'success',
        'data': sorted(trend, key=lambda x: x['date'])
    })

# ============================================
# ROUTES - ML PREDICTIONS
# ============================================

@app.route('/api/predict/demand', methods=['POST'])
def predict_demand():
    """Predict future EV demand"""
    data = request.json
    scenario = data.get('scenario', 'realistic')
    
    predictions = {
        'conservative': {
            2025: 3000000, 2026: 4000000, 2027: 5500000,
            2028: 7000000, 2029: 8500000, 2030: 10000000
        },
        'realistic': {
            2025: 3500000, 2026: 5000000, 2027: 7000000,
            2028: 8500000, 2029: 9500000, 2030: 10000000
        },
        'optimistic': {
            2025: 4000000, 2026: 6000000, 2027: 8000000,
            2028: 9200000, 2029: 9800000, 2030: 10000000
        }
    }
    
    result = predictions.get(scenario, predictions['realistic'])
    
    return jsonify({
        'status': 'success',
        'scenario': scenario,
        'data': result,
        'confidence': 0.85
    })

@app.route('/api/predict/infrastructure', methods=['POST'])
def predict_infrastructure():
    """Predict infrastructure requirements"""
    data = request.json
    target_evs = data.get('target_evs', 5000000)
    
    # Simplified calculation
    stations_needed = int(target_evs / 200)
    chargers_needed = stations_needed * 8
    
    return jsonify({
        'status': 'success',
        'data': {
            'target_evs': target_evs,
            'stations_needed': stations_needed,
            'chargers_needed': chargers_needed,
            'estimated_cost': stations_needed * 50000000  # ₹50 Cr per station
        }
    })

# ============================================
# ROUTES - OPTIMIZATION
# ============================================

@app.route('/api/optimize/locations', methods=['POST'])
def optimize_locations():
    """Get optimized location recommendations"""
    data = request.json
    state = data.get('state')
    budget = data.get('budget', 100000000)
    
    recommendations = {
        'high_priority': [
            {'location': 'Urban Center A', 'roi': 45, 'investment': 50000000},
            {'location': 'Highway Corridor', 'roi': 52, 'investment': 40000000},
            {'location': 'Urban Center B', 'roi': 38, 'investment': 30000000}
        ],
        'medium_priority': [
            {'location': 'Suburban Zone', 'roi': 28, 'investment': 20000000},
            {'location': 'Industrial Area', 'roi': 35, 'investment': 25000000}
        ],
        'implementation_timeline': ['Q1 2026', 'Q2 2026', 'Q3 2026']
    }
    
    return jsonify({
        'status': 'success',
        'state': state,
        'budget': budget,
        'data': recommendations
    })

# ============================================
# ROUTES - SUBSIDIES
# ============================================

@app.route('/api/subsidies/list', methods=['GET'])
def list_subsidies():
    """List available subsidy schemes"""
    subsidies = {
        'PM_E_DRIVE': {
            'name': 'PM E-DRIVE',
            'budget_crore': 10900,
            'subsidy_amount': 150000,
            'eligibility': 'EV buyers in India',
            'status': 'Active'
        },
        'NITI_AAYOG': {
            'name': 'NITI Aayog e-AMRIT',
            'budget_crore': 5000,
            'subsidy_amount': 200000,
            'eligibility': 'Government institutions',
            'status': 'Active'
        }
    }
    
    return jsonify({
        'status': 'success',
        'data': subsidies
    })

@app.route('/api/subsidies/calculate', methods=['POST'])
def calculate_subsidy():
    """Calculate subsidy amount"""
    data = request.json
    ev_cost = data.get('ev_cost', 0)
    scheme = data.get('scheme', 'PM_E_DRIVE')
    
    if scheme == 'PM_E_DRIVE':
        subsidy = min(ev_cost * 0.15, 150000)
    elif scheme == 'NITI_AAYOG':
        subsidy = min(ev_cost * 0.25, 200000)
    else:
        subsidy = 0
    
    return jsonify({
        'status': 'success',
        'ev_cost': ev_cost,
        'subsidy_amount': subsidy,
        'final_cost': ev_cost - subsidy,
        'savings_percentage': round((subsidy / ev_cost * 100), 1) if ev_cost > 0 else 0
    })

# ============================================
# ROUTES - REPORTS
# ============================================

@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """Generate custom report"""
    data = request.json
    report_type = data.get('type', 'summary')
    
    report = {
        'report_id': f"RPT_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'type': report_type,
        'generated_at': datetime.now().isoformat(),
        'data': BACKEND_DATA,
        'summary': f'{report_type.capitalize()} Report - EV Charging Infrastructure'
    }
    
    return jsonify({
        'status': 'success',
        'data': report
    })

# ============================================
# ROUTES - DATA EXPORT
# ============================================

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Export data as CSV"""
    return jsonify({
        'status': 'success',
        'message': 'CSV export ready',
        'format': 'text/csv',
        'records': len(CHARGING_STATIONS)
    })

@app.route('/api/export/json', methods=['GET'])
def export_json():
    """Export data as JSON"""
    return jsonify({
        'status': 'success',
        'message': 'JSON export ready',
        'format': 'application/json',
        'records': len(CHARGING_STATIONS)
    })

# ============================================
# ROUTES - HEALTH CHECK
# ============================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'status': 'success',
        'message': 'EV Charging Infrastructure API is running',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api', methods=['GET'])
def api_info():
    """API information"""
    return jsonify({
        'name': 'EV Charging Infrastructure API',
        'version': '1.0.0',
        'description': 'Backend API for EV Charging Infrastructure Platform',
        'endpoints': {
            'statistics': '/api/statistics',
            'stations': '/api/stations',
            'analytics': '/api/analytics/*',
            'predictions': '/api/predict/*',
            'optimization': '/api/optimize/*',
            'subsidies': '/api/subsidies/*',
            'reports': '/api/reports/*',
            'health': '/api/health'
        }
    })

# ============================================
# ERROR HANDLING
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    print('🚀 Starting EV Charging Infrastructure API Server...')
    print('📊 Backend initialized with:')
    print(f'   - {len(CHARGING_STATIONS)} charging stations')
    print(f'   - {len(STATES)} states coverage')
    print(f'   - {BACKEND_DATA["totalEVs"]:,} EVs in database')
    print('\n✅ API Server running at: http://localhost:5000')
    print('📚 API Documentation at: http://localhost:5000/api')
    print('\nPress CTRL+C to stop the server\n')
    
    app.run(debug=True, host='0.0.0.0', port=5000)
