# PHP-WSGI

### Have you ever wanted to run a php app from the comfort of your trusty python code?  
## No Really?!? _Have You??_

well now you can

```python
# just import our wsgi wrapper 
from php_wsgi.php_app import PhpWsgiApp

if __name__ == "__main__":
    # just create your app, and let it know where to look for files
    app = PhpWsgiApp('my_app')
    # then run like a flask app
    app.run(host='0.0.0.0',port=8888,debug=True)
```

its that easy
