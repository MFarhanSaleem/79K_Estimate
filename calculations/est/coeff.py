# ---------------- Standard coefficients (Pakistan practice) ----------------
import math
BAG_CFT = 1.25            # 1 bag cement (50 kg) = 1.25 cft
DRY_CONC = 1.57           # dry volume factor for concrete (upper end of 1.52-1.57)
DRY_MORTAR = 1.33         # dry volume factor for mortar
BRICKS_PER_CFT = 13.5     # standard local bricks (approx 9 x 4.5 x 3 in) incl. 3/8" joints
MORTAR_PER_CFT = 0.30     # wet mortar per cft of brickwork (upper end of 0.25-0.30; dry = 0.40 cft)
PLASTER_EXTRA = 1.25      # +25% for raked joints / uneven brick surface (upper end)
# wastage (upper-end of standard ranges)
W_CEMENT, W_SAND, W_CRUSH, W_BRICK, W_STEEL, W_PIPE = 0.05, 0.10, 0.05, 0.05, 0.05, 0.10
# rebar unit weight lb/ft  (#2=6mm, #3=10mm, #4=12mm, #5=16mm, #6=20mm)
LB_FT = {2:0.167, 3:0.376, 4:0.668, 5:1.043, 6:1.502}
KG_PER_LB = 0.45359237
MIX = {  # name: (cement, sand, crush)
 '1:2:4':(1,2,4), '1:4:8':(1,4,8), '1:1.5:3':(1,1.5,3), '1:3:6':(1,3,6)}
MORTAR = {'1:6':(1,6), '1:5':(1,5), '1:4':(1,4), '1:3':(1,3)}
def concrete(cft, mix):
    c,s,g = MIX[mix]; t=c+s+g; dry=cft*DRY_CONC
    return dict(cement_bags=dry*c/t/BAG_CFT, sand=dry*s/t, crush=dry*g/t)
def mortar_dry(cft_dry, ratio):
    c,s = MORTAR[ratio]; t=c+s
    return dict(cement_bags=cft_dry*c/t/BAG_CFT, sand=cft_dry*s/t, crush=0.0)
def brickwork(cft, ratio):
    m=mortar_dry(cft*MORTAR_PER_CFT*DRY_MORTAR, ratio)
    m['bricks']=cft*BRICKS_PER_CFT
    return m
def plaster(sqft, thick_in, ratio):
    dry = sqft*thick_in/12.0*DRY_MORTAR*PLASTER_EXTRA
    return mortar_dry(dry, ratio)
def steel_lb(bar, ft): return ft*LB_FT[bar]
def nbars(W_ft, s_in): return math.ceil(W_ft*12.0/s_in)+1
