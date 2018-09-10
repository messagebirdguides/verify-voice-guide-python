# Account Security with Voice 
### ⏱ 15 min build time 

## Why build voice-based account security?

Websites where users can sign up for an account typically use the email address as a unique identifier and a password as a security credential for users to sign in. At the same time, most websites ask users to add a verified phone number to their profile. Phone numbers are, in general, a better way to identify an account holder as a real person. They can also be used as a second authentication factor (2FA) or to restore access to a locked account.

Verification of a phone number is straightforward:

1. Ask your user to enter their number.
2. Call the number programmatically and use a text-to-speech system to say a security code that acts as a one-time-password (OTP).
3. Let the user enter this code on the website or inside an application as proof that they received the call.

The MessageBird Verify API assists developers in implementing this workflow into their apps. Imagine you're running a social network and want to verify your user's profiles. This MessageBird Developer Guide shows you an example of a Python application with integrated account security following the steps outlined above.

By the way, it is also possible to replace the second step with an SMS message, as we explain in this [two factor authentication guide](https://developers.messagebird.com/guides/verify). However, using voice for verification has the advantage that it works with every phone number, not just mobile phones, so it can be used to verify, for example, the landline of a business. The [MessageBird Verify API](https://developers.messagebird.com/docs/verify) supports both options; voice and SMS.

## Getting Started

Our sample application is built in Python using the [Flask](http://flask.pocoo.org/) framework. You can download or clone the complete source code from the [MessageBird Developer Guides GitHub repository](https://github.com/messagebirdguides/verify-voice-guide-python) to run the application on your computer and follow along with the guide.

We assume that you already have Python and the Python package manager pip installed. Using pip, you can install the [Python client for the MessageBird REST API](https://github.com/messagebird/python-rest-api) and Flask with the following two commands:

````bash
pip install messagebird
pip install Flask
````

To handle our forms, we will use the [WTForms](https://wtforms.readthedocs.io/en/stable/) forms rendering library and the [Flask-WTF library](https://flask-wtf.readthedocs.io/en/stable/), which integrates WTForms with Flask. Install these libraries with the following commands:

````bash
pip install WTForms
pip install Flask-WTF
````

## Configuring the MessageBird REST API

To run the code, you need to provide a MessageBird API key. One way to do so is through a configuration file that is separate from the main application code. We've prepared a `config_file.cfg ` file in the repository, which you should edit to include your API key. The file has the following format:

````env
SECRET_KEY=YOUR-API-KEY
````
You can include more configuration variables in this file. For example, adding a `DEBUG=True` line will facilitate troubleshooting when you test your application. 

You can create or retrieve a live API key from the [API access (REST) tab](https://dashboard.messagebird.com/en/developers/access) in the _Developers_ section of your MessageBird account.

To load this key into the application, we initialize the application and load the key from the `config_file.cfg`:

````python
app = Flask(__name__)
app.config.from_pyfile('config_file.cfg')
````

Then, let's create an instance of the MessageBird Python client:

````Python
client = messagebird.Client(app.config['SECRET_KEY'])
````

## Asking for the Phone Number

The sample application contains a form to collect the user's phone number. You can see the HTML as a Jinja2 template in the file `templates/index.html`:

````html
  <h1>MessageBird Verify Example</h1>
  <p>Enter your phone number:</p>
  <form action="{{ url_for('submitPhone') }}" method="post">
  <dl>
  {{ initial_form.number }}
  {{ initial_form.submit }}
  </dl>
  </form>
````

The route that renders the form is defined under `@app.route('/', methods=['GET', 'POST'])` in `app.py`. The route starts by instantiating the two forms used in the application. 

````python
@app.route('/', methods=['GET', 'POST'])
def submitPhone():
    initial_form = SubmitPhoneNumber(request.form)
    code_form = EnterCode()
````
The two forms instantiated are defined in `forms.py`.
The form for obtaining the phone number, `initial_form`, has a structure  defined by the  class `SubmitPhoneNumber`:

````python
class SubmitPhoneNumber(FlaskForm):
    number = TelField('Phone number')
    submit = SubmitField('Send code')
````

The form has a `Telfield` type field for collecting the phone number and a submit button. Once the user clicks on that button, the input is sent to the `submitPhone()` function defined under `@app.route('/', methods=['GET', 'POST'])` in `app.py`.


## Initiating the Verification Call

When the user submits their phone number, the `submitPhone()` function sends it to the MessageBird API using the `verify_create()` method. The Verify API expects the user's telephone number to be in international format, so when you test the code, make sure to include the country code in the form.

````python
#when form is posted, try to obtain server response
if request.method=="POST":
    try:
        verify = client.verify_create(initial_form.number.data,
                                      {'type':'tts',
                                       'template': 'Your security code is %token.'})
        #on success we render verify.id on the hidden field on the verification page (/EnterCode)
        return redirect(url_for('enterCode', code_form=code_form, verify_id=verify.id))
        
````

The `verify.create()` call takes the phone number entered in the form (`initial_form.number.data`) and two other parameters:

- The `type` parameter is set to `tts` to inform the API that we want to use a voice call for verification.
- The `template` parameter contains the words to speak. It must include the placeholder `%token` so that MessageBird knows where the code goes (note that we use the words "token" and "code" interchangeably, they mean the same thing). We don't have to generate this numeric code ourselves; the API takes care of it.

There are a few other available options. For example, you can change the length of the code (it defaults to 6) by specifying the optional parameter `tokenLength`. You can also specify `voice` as `male` or `female` and set the `language` to an ISO language code if you want the synthesized voice to be in a non-English language. You can find more details about these and other options in the [Verify API reference documentation](https://developers.messagebird.com/docs/verify#request-a-verify).

If the `verify_create()` call succeeds, we redirect the user to the page where they can enter the verification code they will receive in the voice call. This page is represented by the `/EnterCode` route in `app.py`. The `id` attribute of the `verify` object returned by the call is passed into the route, as it is required to determine which object the verification code corresponds to.

If our `verify_create()` call leads to an error, we flash an error message at the top of the page:

````python
#on failure, render description for error on same page.
except messagebird.client.ErrorException as e:
    for error in e.errors:
        flash('  description : %s\n' % error.description)
    return render_template('index.html', initial_form=initial_form)
````

The region where the error will flash is defined in the `index.html` template as follows:

````html
<!--If form submission results in error, flash error message -->
{% with messages = get_flashed_messages() %}
  {% if messages %}
    <ul class=flashes>
    {% for message in messages %}
      <li>{{ message }}</li>
    {% endfor %}
    </ul>
  {% endif %}
{% endwith %}
````

## Confirming the Code

The template stored in `templates/entercode.html`, which we render in the success case, contains an HTML form with a hidden input field to pass forward the `id` from the verification request. It also contains a visible text field in which the user can enter the code that they've heard on the phone. When the user submits this form, it sends this token to the `/success` route.

````html
  <h1>Enter your verification code</h1>
  <form action="{{ url_for('enterCode', code_form=code_form, verify_id=code_form.verify_id.data) }}" method="post">
    <dl>
    {{ code_form.verify_id }}
    {{ code_form.token }}
    {{ code_form.submit }}
    </dl>
  </form>
````

The structure of the `code_form` object referenced in the template is defined by the `EnterCode` class in `forms.py`:

````python
class EnterCode(FlaskForm):
    verify_id = HiddenField('ID')
    token = StringField('Enter your verification code:')
    submit = SubmitField('Check code')
````

In the main file, `app.py`, the `enterCode()` function defines what happens when the page is loaded, and when the verification code is submitted. When the page loads, the form is instantiated, and the hidden field reserved for the ID is filled with the argument that is passed into `enterCode()`:

````python
#What happens when you submit the verification form
@app.route('/EnterCode/<verify_id>', methods=['GET', 'POST'])
def enterCode(verify_id):
    code_form = EnterCode(request.form)
    code_form.verify_id.data = verify_id
````

When the form is posted, we call another method in the MessageBird API, `verify_verify()`, and provide the ID and token as two parameters. Upon success, we redirect the user to a success page, which is defined by the `/success` route.

````python
#when form is posted, try to obtain server response
if  request.method=="POST":
    try:
        verify = client.verify_verify(code_form.verify_id.data, code_form.token.data)
        #on success, render a (new) success page.
        return render_template('success.html')
````

On a failure, we flash an error message at the top of the page. 

````python
#on failure, flash error description on same page.
except messagebird.client.ErrorException as e:
    for error in e.errors:
        flash('  description : %s\n' % error.description)
    return redirect(url_for('enterCode', code_form=code_form, verify_id=verify_id))
````
The region for flashing error messages is defined in `entercode.html` as follows:

````html
<!--If error received upon form submission, flash error message at top -->
<!--of page -->
{% with messages = get_flashed_messages() %}
  {% if messages %}
    <ul class=flashes>
    {% for message in messages %}
      <li>{{ message }}</li>
    {% endfor %}
    </ul>
  {% endif %}
{% endwith %}
````

The success page that the user sees after submitting a correct verification code is defined by the `success.html` template:

````html
<html>
  <head>
    <title></title>
  </head>
  <body>
    <p>You have successfully verified your phone number.</p>
  </body>
</html>
````
The route for the success page, defined in `app.py`, is simple:

````python
#success page; displayed if correct verification code is entered
@app.route('/success')
def success():
    return render_template('success.html')
````

## Testing the Application

Great, you've reached the end of this guide! This is all you have to do to verify a phone number! Let's test whether your application works. Check again that you have provided a live API key in `config_file.cfg`. Then, in the project folder, enter the following command in your console:

````bash
python app.py
````

Now, open your browser to http://localhost:5000/ and walk through the process yourself.

## Nice Work!

You now have a running integration of MessageBird's Verify API!

You can now leverage the flow, code snippets and UI examples from this tutorial to build your own voice-based account security system. Don't forget to download the code from the [MessageBird Developer Guides GitHub repository](https://github.com/messagebirdguides/verify-voice-guide-python).

## Next Steps

Want to build something similar but not quite sure how to get started? Please feel free to let us know at support@messagebird.com, we'd love to help!

