import math
import numpy as np
import cv2
import urllib.request
import sys
from collections import OrderedDict

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
    return 256 << levelOfDetail

'''
    Determines the ground resolution (in meters per pixel) at a specified latitude and level of detail.
    latitude = float
    levelOfDetail = int
    
    returns The ground resolution, in meters per pixel
'''
def groundResolution(latitude,levelOfDetail):
    latitude = clip(latitude,MINLATITUDE,MAXLATITUDE)
    return np.cos(latitude*math.pi/180) * 2 * np.pi * EARTHRADIUS/mapSize(levelOfDetail)

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
    sinLatitude = np.sin(latitude*np.pi/180)
    y = 0.5 - np.log((1 + sinLatitude) / (1 - sinLatitude))/(4*math.pi)
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
    tileX = np.floor(pixelX/256)
    tileY = np.floor(pixelY/256)
    return int(tileX),int(tileY)

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
    quadKey = []
    i = levelOfDetail
    while i > 0:
        digit = 0
        mask = 1 << (i-1)
        if (tileX & mask) != 0:
            digit = digit + 1
            #digit = str(digit)
        if (tileY & mask) != 0:
            digit = digit + 1
            digit = digit + 1
            #digit = str(digit)
        quadKey.append(str(digit))
        i -= 1
    return ''.join(quadKey)

'''
    Converts a QuadKey into tile XY coordinates.
    quadKey = QuadKey of tile
    tileX = Tile X coordinate
    tileY = Tile Y coordinate
        
    returns levelOfDetail         
'''
def quadKey2TileXY(quadKey):
    tileX = 0
    tileY = 0
    levelOfDetail = len(quadKey)

    i = levelOfDetail
    try:
        while i > 0:
            mask = 1 << (i-1)
            if quadKey[levelOfDetail - i] == '1':
                tileX = tileX | mask
            elif quadKey[levelOfDetail - i] == '2':
                tileY = tileY | mask
            elif quadKey[levelOfDetail - i] == '3':
                tileX = tileX | mask
                tileY = tileY | mask
            i -= 1
    except:
        print("Invalid quad key")

    return tileX,tileY

'''
    Given a quadkey we will get the image from the url
    
    
    
    CodeRef = http://www.pyimagesearch.com/2015/03/02/convert-url-to-image-with-python-and-opencv/
'''
def get_image_from_quadkey(quadKey):
    url = "http://h0.ortho.tiles.virtualearth.net/tiles/h%s.jpeg?g=131" %(str(quadKey))
    response = urllib.request.urlopen(url)
    image = np.asarray(bytearray(response.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    return image

def add_zoom_to_tiles(dummy_tiles,startTileZoomLevel):

    for tile in dummy_tiles:
        temp = startTileZoomLevel
        while temp > 0:
            temp_quadKey = tileXY2QuadKey(tile[0],tile[1],temp)
            temp_img = get_image_from_quadkey(temp_quadKey)
            cv2.imwrite('sample.jpeg',temp_img)
            sample = np.array(cv2.imread('sample.jpeg'))
            if error.shape == sample.shape and not (np.bitwise_xor(error, sample).any()):
                temp -= 1
                continue
            else:
                startTileZoomLevel = temp
                tile_dict[tile] = temp

                break


#
# args = sys.argv
# if len(args) < 4:
#     print("USAGE: python Retrive_aerial.py lat1 lng1 lat2 lng2")
#     exit(1)

initialZoomLevel = 23
error = np.array(cv2.imread('error.jpeg'))
tile_2d = []
dummy_tiles = []
tile_dict = OrderedDict()


while initialZoomLevel > 0:
    start_PixelX, start_PixelY = latLong2pixelXY(float(41.882692), float(-87.623332), initialZoomLevel)
    end_PixelX, end_PixelY = latLong2pixelXY(float(41.883692), float(-87.625332), initialZoomLevel)

    start_TileX, start_TileY = pixelXY2tileXY(start_PixelX, start_PixelY)
    end_TileX, end_TileY = pixelXY2tileXY(end_PixelX, end_PixelY)

    min_start_tile = min((start_TileX, start_TileY), (end_TileX, end_TileY))
    max_end_tile = max((start_TileX, start_TileY), (end_TileX, end_TileY))

    quadKey = tileXY2QuadKey(min_start_tile[0], min_start_tile[1], initialZoomLevel)
    img = get_image_from_quadkey(quadKey)

    cv2.imwrite('sample.jpeg',img)
    sample = np.array(cv2.imread('sample.jpeg'))

    if error.shape == sample.shape and not(np.bitwise_xor(error,sample).any()):
        initialZoomLevel -= 1
        continue
    else:
        startTileZoomLevel = initialZoomLevel
        tile_dict[min_start_tile] = startTileZoomLevel
        for j in range(min_start_tile[0], max_end_tile[0] + 1):
            tile_list = []
            for k in range(min_start_tile[1], max_end_tile[1] + 1):
                tile_list.append((j, k))
                dummy_tiles.append((j,k))
            tile_2d.append(tile_list)

        break

add_zoom_to_tiles(dummy_tiles,startTileZoomLevel)
min_zoom_level = min(tile_dict.values())

for key,value in tile_dict.items():
    tile_dict[key] = min_zoom_level

print(tile_dict)