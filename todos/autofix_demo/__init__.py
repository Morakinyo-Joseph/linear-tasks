"""
Multi-layer intentional error demos for Insider auto-fix.

DEBUG-only HTTP surfaces that cross views → serializers → services → utils
so a single boom yields a deeper stack than ``demo_views.BoomView``.
"""
