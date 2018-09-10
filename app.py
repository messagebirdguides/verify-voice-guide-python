from flask import Flask, render_template, request, flash, url_for, redirect
#imports the two forms we have defined in forms.py
from forms import SubmitPhoneNumber, EnterCode
import messagebird

#Configure the app as follows.
app = Flask(__name__)
app.config.from_pyfile('config_file.cfg')

#create instance of messagebird.Client using API key
client = messagebird.Client(app.config['SECRET_KEY'])

#What happens when the user submits their phone number
@app.route('/', methods=['GET', 'POST'])
def submitPhone():
    initial_form = SubmitPhoneNumber(request.form)
    code_form = EnterCode()

    #when form is posted, try to obtain server response
    if request.method=="POST":
        try:
            verify = client.verify_create(initial_form.number.data,
                                          {'type':'tts',
                                           'template': 'Your security code is %token.'})
            #on success we render verify.id on the hidden field on the verification page (/EnterCode)
            return redirect(url_for('enterCode', code_form=code_form, verify_id=verify.id))
        
        #on failure, render description for error on same page.
        except messagebird.client.ErrorException as e:
            for error in e.errors:
                flash('  description : %s\n' % error.description)
            return render_template('index.html', initial_form=initial_form)

    return render_template('index.html', initial_form=initial_form)


#What happens when you submit the verification form
@app.route('/EnterCode/<verify_id>', methods=['GET', 'POST'])
def enterCode(verify_id):
    code_form = EnterCode(request.form)

    #prefill verify ID in hidden field
    code_form.verify_id.data = verify_id
    
    #when form is posted, try to obtain server response
    if  request.method=="POST":
        try:
            verify = client.verify_verify(code_form.verify_id.data, code_form.token.data)
            #on success, render a (new) success page.
            return render_template('success.html')
        #on failure, flash error description on same page.
        except messagebird.client.ErrorException as e:
            for error in e.errors:
                flash('  description : %s\n' % error.description)
            return redirect(url_for('enterCode', code_form=code_form, verify_id=verify_id))

    return render_template('entercode.html', code_form=code_form, verify_id=verify_id)

#success page; displayed if correct verification code is entered
@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    app.run()
