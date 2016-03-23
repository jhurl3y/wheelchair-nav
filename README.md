# wheelchair-nav
GPS-based Autonomous Wheelchair Server Code

This code is part of my final year project in Electronic and Computer Engineering in NUI Galway, Ireland. The aim of this project is to design a GPS-based autonomous system for wheelchair users. I have built a prototype (not an actual wheelchair) to test the feasibilty of such a system (see pictures below).

<img src="/pictures/1.jpg?raw=true" alt="alt text" width="300x">
<img src="/pictures/2.jpg?raw=true" alt="alt text" width="300x">
<img src="/pictures/3.jpg?raw=true" alt="alt text" width="300x">
<img src="/pictures/4.jpg?raw=true" alt="alt text" width="300x">

A complete guide (including circuit diagrams, necessary software installation steps, relevant instructions) will be added on completion. 

This repo contains the server code running on the Raspberry Pi Model B+ which communicates with the accompanying [Android App](https://github.com/jhurl3y/FindMyWay) over Bluetooth. This code is responsible for driving the motors, taking IMU/GPS readings, filtering data and sending information back and forth between the prototype system and mobile phone.
