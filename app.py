from flask import Flask, render_template, request, redirect
import pandas as pd
import os
from datetime import datetime, timedelta

app = Flask(__name__)

def create_proper_excel_template():
    base_date = datetime(2025, 3, 3)
    columns = [
        'Date', 'Day', 'Wake up at 6:00 AM', 'Drink 500ml water',
        'Cold Shower', 'Meditation', 'Journaling', 'Reading',
        'Skill Learning', 'Stretching Mobility', 'Strength Training',
        'Cardio Workout', 'Reached 10K+ steps', 'Clean Eating',
        'No Sugar', 'No Alcohol', '4L Water Intake', 'Healthy Breakfast',
        'Sleep by 10:00 PM', 'Diet compliance', 'Fitness completion',
        'Mental Wellness', 'Daily completion score', 'Streak'
    ]
    
    dates = [base_date + timedelta(days=i) for i in range(75)]
    df = pd.DataFrame({
        'Date': dates,
        'Day': [(base_date + timedelta(days=i)).strftime('%A') for i in range(75)],
    })
    
    # Initialize all task columns as False
    for col in columns[2:-4]:  # Exclude score columns
        df[col] = False
    
    # Initialize score columns
    df['Diet compliance'] = 0.0
    df['Fitness completion'] = 0.0
    df['Mental Wellness'] = 0.0
    df['Daily completion score'] = 0.0
    df['Streak'] = 0

    # Create Excel file with explicit sheet name
    with pd.ExcelWriter('Sample_75_Day Hard Routine_tracker.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Daily Tracker', index=False)
    
    print("Excel template created with sheet 'Daily Tracker'")  
    
# Excel-like calculations
def calculate_scores(row):
    # Diet Compliance (N2:R2)
    diet_cols = ['Clean Eating', 'No Sugar', 'No Alcohol', 
                '4L Water Intake', 'Healthy Breakfast']
    diet_score = sum(row[col] for col in diet_cols) / 5
    
    # Fitness Completion (J2:M2)
    fitness_cols = ['Stretching Mobility', 'Strength Training', 
                   'Cardio Workout', 'Reached 10K+ steps']
    fitness_score = sum(row[col] for col in fitness_cols) / 4
    
    # Mental Wellness (E2:I2)
    mental_cols = ['Cold Shower', 'Meditation', 'Journaling',
                  'Reading', 'Skill Learning']
    mental_score = sum(row[col] for col in mental_cols) / 5
    
    # Daily Completion (C2:S2) - 17 tasks
    daily_tasks = ['Wake up at 6:00 AM', 'Drink 500ml water'] + mental_cols + fitness_cols + diet_cols
    daily_score = sum(row[col] for col in daily_tasks) / 17
    
    return diet_score, fitness_score, mental_score, daily_score

def update_streak(df):
    # Implement streak calculation
    df['Streak'] = 0
    current_streak = 0
    for idx, row in df.iterrows():
        if row['Daily completion score'] == 1:
            current_streak += 1
        else:
            current_streak = 0
        df.at[idx, 'Streak'] = current_streak
    return df

@app.route('/')
def home():
    try:
        if not os.path.exists('Sample_75_Day Hard Routine_tracker.xlsx'):
            create_proper_excel_template()
        
        # Verify sheet exists
        xl = pd.ExcelFile('Sample_75_Day Hard Routine_tracker.xlsx')
        if 'Daily Tracker' not in xl.sheet_names:
            raise ValueError(f"Sheet 'Daily Tracker' missing. Found sheets: {xl.sheet_names}")
            
        df = pd.read_excel(xl, sheet_name='Daily Tracker', parse_dates=['Date'])
        
        df = pd.read_excel('Sample_75_Day Hard Routine_tracker.xlsx',
                          sheet_name='Daily Tracker')
        print("Columns found:", df.columns.tolist())
        df = update_streak(df)  # Calculate streaks on load
        return render_template('index.html', days=df.to_dict('records'))
    except Exception as e:
        return f"Error loading data: {str(e)}", 500

@app.route('/update/<date>', methods=['POST'])
def update_day(date):
    print(f"\nUpdating date: {date}")
    
    df = pd.read_excel('Sample_75_Day Hard Routine_tracker.xlsx', 
                      sheet_name='Daily Tracker',
                      parse_dates=['Date'])
    
    # Find matching date
    target_date = pd.to_datetime(date)
    mask = df['Date'] == target_date
    
    # Update all task columns
    task_columns = [
        'Wake up at 6:00 AM', 'Drink 500ml water', 'Cold Shower',
        'Meditation', 'Journaling', 'Reading', 'Skill Learning',
        'Stretching Mobility', 'Strength Training', 'Cardio Workout',
        'Reached 10K+ steps', 'Clean Eating', 'No Sugar', 'No Alcohol',
        '4L Water Intake', 'Healthy Breakfast', 'Sleep by 10:00 PM'
    ]
    
    for col in task_columns:
        df.loc[mask, col] = request.form.get(col, 'off') == 'on'
    
    # Calculate scores
    diet, fitness, mental, daily = calculate_scores(df.loc[mask].iloc[0])
    df.loc[mask, 'Diet compliance'] = diet
    df.loc[mask, 'Fitness completion'] = fitness
    df.loc[mask, 'Mental Wellness'] = mental
    df.loc[mask, 'Daily completion score'] = daily
    
    print("Updated values:", df.loc[mask, task_columns])
    
    # Update streak for all rows
    df = update_streak(df)
    
    # Save back to Excel
    df.to_excel('Sample_75_Day Hard Routine_tracker.xlsx', 
               sheet_name='Daily Tracker', 
               index=False,
               engine='openpyxl')
    
    return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)