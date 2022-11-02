#!/usr/bin/env python3
# import os

from aws_cdk import App

from cdk.stack import AppStack

app = App()
AppStack(
    app,
    "AppStack",
)

app.synth()
