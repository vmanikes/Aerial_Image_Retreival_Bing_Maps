import math

EARTHRADIUS = 6378137
MINLATITUDE = -85.05112878
MAXLATITUDE = 85.05112878
MINLONGITUDE = -180
MAXLONGITUDE = 180

#All params are in float
'''
    Clips a number to the specified minimum and maximum values
    n = The number to clip
    minValue = Minimum allowable value
    maxValue = Maximum allowable value
    
    returns The clipped value
'''
def clip(n,minValue,maxValue):
    return min(max(n,minValue),maxValue)

'''
    Determines the map width and height (in pixels) at a specified level of detail.
    levelOfDetail = Level of detail, from 1 (lowest detail) to 23 (highest detail)
    
    returns The map width and height in pixels.
'''
def mapSize(levelOfDetail):
    pass

'''
    Determines the ground resolution (in meters per pixel) at a specified latitude and level of detail.
    latitude = float
    levelOfDetail = int
    
    returns The ground resolution, in meters per pixel
'''
def groundResolution(latitude,levelOfDetail):
    latitude = clip(latitude,MINLATITUDE,MAXLATITUDE)
    return math.cos(latitude*math.pi/180) * 2 * math.pi * EARTHRADIUS/mapSize(levelOfDetail)

'''
    Determines the map scale at a specified latitude, level of detail, and screen resolution.
    
    latitude = Latitude (in degrees) at which to measure the map scale.
    levelOfDetail = Level of detail, from 1 (lowest detail) to 23 (highest detail). (int)
    DPI = Resolution of screen in Dots per inch
    
    returns The map scale, expressed as the denominator N of the ratio 1 : N
'''
def mapScale(latitude,levelOfDetail,screenDPI):
    return groundResolution(latitude,levelOfDetail) * screenDPI/0.0254

'''
    Converts a point from latitude/longitude WGS-84 coordinates (in degrees) into pixel XY coordinates at a specified level of detail.
    
    latitude = Latitude of the point, in degrees.
    longitude = Longitude of the point, in degrees.
    levelOfDetail = Level of detail, from 1 (lowest detail) to 23 (highest detail). (int)
    
    return pixelX and pixelY
'''
def latLong2pixelXY(latitude,longitude,levelOfDetail):
    latitude = clip(latitude,MINLATITUDE,MAXLATITUDE)
    longitude = clip(longitude,MINLONGITUDE,MAXLONGITUDE)

    x = (longitude + 180)/360.0
    sinLatitude = math.sin(latitude*math.pi/180)
    y = 0.5 - math.log((1 + sinLatitude) / (1 - sinLatitude))/(4*math.pi)
    mapSize1 = mapSize(levelOfDetail)
    pixelX = int(clip(x * mapSize1 + 0.5, 0, mapSize1 - 1))
    pixelY = int(clip(y * mapSize1 + 0.5, 0, mapSize1 - 1))

    return pixelX,pixelY

'''
    Converts a pixel from pixel XY coordinates at a specified level of detail into latitude/longitude WGS-84 coordinates (in degrees).
    
    pixelX = X coordinate of the point, in pixels.
    pixelY = Y coordinates of the point, in pixels.
    levelOfDetail = Level of detail, from 1 (lowest detail) to 23 (highest detail). (int)
    
    returns latitude and longitude
'''
def pixelXY2LatLng(pixelX,pixelY,levelOfDetail):
    mapSize1 = mapSize(levelOfDetail)
    x = (clip(pixelX,0,mapSize1-1)/mapSize1) - 0.5
    y = 0.5 - (clip(pixelY,0,mapSize1-1)/mapSize1)

    latitude = 90 - 360 * math.atan(math.exp(-y * 2 * math.pi))/math.pi
    longitude = 360 * x

    return latitude,longitude

'''
   Converts pixel XY coordinates into tile XY coordinates of the tile containing the specified pixel. 
   pixelX = X coordinate of the point, in pixels.
   pixelY = Y coordinates of the point, in pixels.
   
   return tileX and tileY 
'''
def pixelXY2tileXY(pixelX,pixelY):
    tileX = pixelX/256
    tileY = pixelY/256
    return tileX,tileY

'''
    Converts tile XY coordinates into pixel XY coordinates of the upper-left pixel of the specified tile.
    tileX = Tile X coordinate
    tileY = Tile Y coordinate
    
    return pixelX,pixelY
'''
def tileXY2PixelXY(tileX,tileY):
    pixelX = tileX * 256
    pixelY = tileY * 256

    return pixelX,pixelY

'''
    Converts tile XY coordinates into a QuadKey at a specified level of detail.
    tileX = Tile X coordinate
    tileY = Tile Y coordinate
    levelOfDetail = Level of detail, from 1 (lowest detail) to 23 (highest detail). (int)
    
    returns a string containing the quad key
'''
def tileXY2QuadKey(tileX,tileY,levelOfDetail):
    pass

'''
    Converts a QuadKey into tile XY coordinates.
    quadKey = QuadKey of tile
    tileX = Tile X coordinate
    tileY = Tile Y coordinate
    
    
    returns levelOfDetail 
    
        
'''
def quadKey2TileXY(quadKey):
    pass