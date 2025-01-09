![logo](https://github.com/progame1201/VoiceSockets/blob/master/imgs/vcm.png)
# VoiceSockets
It is a voice chat for communicating with people, written entirely in python. encryption included.
# What do I need to launch?
You need python version 3.12 and modules from `requirements.txt`<br>
``pip install -r requirements.txt``<br>
also look into the config and configure the ip, port, password, and key path there.<br>
key can be generated in server/keygen.py<br>
# How many people support VoiceSockets?
I ran up to 9 clients locally, everything worked fine. *most likely it can support more than 9 clients.*
# How safe is it?
All data is encrypted with AES encryption in CBC mode using the PyCryptodome module. <br>
It is important to note that encrypted data is serialized using json, but classes are serialized using pickle.
# What are the features here?
You can mute yourself (shift+v by default or button) as well as mute someone else.<br>
There are channels you can join (by default, there are two).<br>
At startup, you can set up a microphone and set a nickname.<br>
There is a noise gate of the data being sent, which can be configured in the config<br>
