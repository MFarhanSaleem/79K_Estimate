# Ground floor / foundation wall centerline network (feet). Origin: back-left extreme of building
# (x to the right, y towards the FRONT/road). Derived from structural drawing S-01 vector lines.
# (id, x1,y1,x2,y2, thickness_ft, foundation_type, description)
W = [
 # ---- 9" walls ----
 ("R1", 17.376,0.375, 36.881,0.375, 0.75, 2, "Back wall (Bed-1 & S-T lobby) facing rear passage"),
 ("R2", 17.376,0.375, 17.376,3.688, 0.75, 2, "Back wall step (S-T lobby, rear)"),
 ("R3", 23.131,0.375, 23.131,13.938, 0.75, 3, "S-T lobby / Bed-1 partition"),
 ("R4", 17.380,9.250, 23.131,9.250, 0.75, 3, "S-T lobby / lobby partition"),
 ("R5", 17.380,7.563, 17.380,25.501, 0.75, 3, "Bath-Dress & M-Bed / lobby partition"),
 ("R6", 3.896,3.688, 3.896,12.750, 0.75, 2, "Left outer wall of stair & bath"),
 ("R6b",2.626,12.750, 3.896,12.750, 0.75, 2, "Left outer wall jog"),
 ("R7", 2.626,12.750, 2.626,25.501, 0.75, 2, "M-Bed left outer wall"),
 ("R8", 1.000,25.501, 18.255,25.501, 0.75, 3, "M-Bed / kitchens partition"),
 ("R9", 1.376,25.501, 1.376,37.252, 0.75, 2, "Raw kitchen left outer wall"),
 ("R10",0.375,37.252, 9.125,37.252, 0.75, 3, "Raw kitchen / TV lounge partition"),
 ("R11",0.375,37.252, 0.375,51.095, 0.75, 2, "TV lounge left outer wall"),
 ("R12",0.375,51.095, 3.436,50.002, 0.75, 2, "TV lounge front splayed wall"),
 ("R13",3.436,50.002, 16.130,50.002, 0.75, 2, "TV lounge front wall"),
 ("R14",16.130,41.502, 16.130,50.002, 0.75, 2, "TV lounge / entrance wall"),
 ("R15",16.130,45.252, 23.131,45.252, 0.75, 2, "Entrance front wall"),
 ("R16a",23.131,19.314, 23.131,42.252, 0.75, 3, "Lobby / dining-drawing partition"),
 ("R16b",23.131,42.252, 23.131,46.002, 0.75, 2, "Lobby / car-porch wall"),
 ("R17",23.131,42.252, 36.881,42.252, 0.75, 2, "Drawing room front wall (car porch)"),
 ("R18a",36.881,0.375, 36.881,19.501, 0.75, 1, "Right property-line wall (rear part)"),
 ("R18b",36.881,29.314, 36.881,50.503, 0.75, 1, "Right property-line wall (front part)"),
 ("R19",32.881,19.501, 36.881,19.501, 0.75, 2, "Patio top wall"),
 ("R20",32.881,19.501, 32.881,24.251, 0.75, 2, "Patio left wall"),
 ("R21",32.881,24.251, 37.069,24.251, 0.75, 2, "Patio bottom / P-W top wall"),
 # ---- 4.5" walls ----
 ("G1", 3.896,3.688, 17.376,3.688, 0.375, 4, "Stair hall rear wall (to back car porch)"),
 ("G2", 3.896,7.563, 17.380,7.563, 0.375, 4, "Stair / bath-dress partition"),
 ("G3", 3.896,12.938, 17.380,12.938, 0.375, 4, "Bath-dress / M-Bed partition"),
 ("G4", 12.318,7.563, 12.318,12.938, 0.375, 4, "Bath / dress partition"),
 ("G5", 23.131,13.938, 36.881,13.938, 0.375, 4, "Bed-1 / dress-bath partition"),
 ("G6", 22.943,13.938, 22.943,19.314, 0.375, 4, "Lobby / dress partition"),
 ("G7", 22.943,19.314, 32.881,19.314, 0.375, 4, "Dress-bath / dining partition"),
 ("G8", 27.318,13.938, 27.318,19.314, 0.375, 4, "Dress / bath partition"),
 ("G9", 8.938,25.501, 8.938,37.252, 0.375, 4, "Raw kitchen / open kitchen partition"),
 ("G10",32.694,24.251, 32.694,29.314, 0.375, 4, "P-W left wall"),
 ("G11",32.694,29.314, 36.881,29.314, 0.375, 4, "P-W front wall"),
 ("G12",37.069,24.251, 37.069,29.314, 0.375, 4, "P-W right (property-line) wall"),
 ("G13",3.501,50.565, 4.625,50.565, 0.375, 4, "Front elevation projection"),
 ("G14",13.130,50.565, 16.505,50.565, 0.375, 4, "Front elevation projection"),
]
# extras (plan area sq ft): piers / nibs not captured by centerlines
EXTRA = [("P1","Front-right corner pillar 13.5x13.5 in",1.125*1.124),
         ("P2","Pier at raw-kitchen corner 4.5x18 in",0.375*1.5),
         ("P3","Nib at car-porch wall end",0.375*0.375)]
