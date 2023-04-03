# include routes
from flask import Blueprint, render_template, request, flash, jsonify,redirect, url_for
from flask_login import login_required, current_user
from .models import Note, Transaction
from . import db
import json
from sqlalchemy import func

views = Blueprint('views',__name__)

@views.route('/',methods = ['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 
        users = request.form.get('users')#Gets the note from the HTML 
        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id, users=users)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/event/<eventid>',methods = ['GET', 'POST'])
@login_required
def event(eventid):
    if request.method == 'GET': 
        print(eventid)
        note = Note.query.get(eventid)
        cost = view_transaction(eventid)
        result_dict = check_balance(eventid)

        return render_template("event.html", user=current_user,event=note, cost = cost,result_dict=result_dict)
    if request.method == 'POST': 
        print('posting')
        return render_template("event.html", user=current_user,event=note)


def check_balance(eventid):
    print('checking balance...')
    result = db.session.query(Transaction.user_name, db.func.sum(Transaction.amount)).filter_by(note_id=eventid).group_by(Transaction.user_name).all()
    result_dict = {username: round(amount,2) for username, amount in result}
    print(result_dict)
    return result_dict

@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


def view_transaction(noteid):  
    trans = Note.query.get(noteid).transactions
    cost = 0
    for i in trans:
        if i.amount < 0:
            cost = cost + i.amount
    return -cost


@views.route('/add-trans', methods=['POST'])
def add_trans():  
    print('adding new trans')
    noteId  = request.form.get('event')
    trans = request.form.get('transaction')
    user = request.form.get('users')
    payer = request.form.get('payer')
    alluser = user.split(';')
    for i in alluser:
        identify_user(i, noteId)
        new_trans= Transaction(note_id = noteId, amount = float(trans)/len(alluser), user_name = i)
        db.session.add(new_trans)
        db.session.commit()
    
    new_trans2= Transaction(note_id = noteId, amount = -float(trans), user_name = payer)
    db.session.add(new_trans2)
    db.session.commit()
    return redirect(url_for('views.home'))

def identify_user(user, eventId):
    print('identifying...')
    note = Note.query.get(eventId)
    users1 = note.users
    users = users1.split(';')
    if user in users:
        return 
    else:
        # add user into the note database
        note.users = users1 + ';' + user
        db.session.commit()
        return
