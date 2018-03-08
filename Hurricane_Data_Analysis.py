"""
IS5 Hurricane Data Analysis
By: Rahul Kumra
"""

from collections import Counter
from pygeodesy import ellipsoidalVincenty as ev
import datetime


def storm_name(record: str) ->str:
    """
    Return the name of a storm if it is not 'UNNAMED'.
    :param record: the first row of a storm
    :return: name of the storm or none (When it is UNNAMED)
    """
    name = record.split(',')[1].strip()
    if not name == 'UNNAMED':
        return name


def storm_id(record: str) ->str:
    """
    Return the id of the storm
    :param record: the first row of a storm
    :return: id of the storm.
    """
    return record.split(',')[0].strip()


def is_landfill(record: str) ->bool:
    """
    Determine whether there is a landfill.
    :param record: one line of the record.
    :return: True is there is a landfill, false if there is not a landfill.
    """
    return record.split(',')[2].strip() == 'L'


def is_hurricane(record: str) ->bool:
    """
    Determine whether there is a hurricane.
    :param record: one line of the record.
    :return: True is there is a hurricane, false if there is not a hurricane.
    """
    return record.split(',')[3].strip() == 'HU'


def wind(record: str) -> int:
    """
    Find the level of the wind.
    :param record: one line of the record.
    :return: The level of the wind.
    """
    return int(record.split(',')[6].strip())


def year_of(record) -> int:
    """
    Find the year of the record.
    :param record: one line of the record.
    :return: The year of the record occured.
    """
    return int(record[:4])


def flip_direction(direction: str) -> str:
    """Given a compass direction 'E', 'W', 'N', or 'S', return the opposite.
    Raises exception with none of those.

    :param direction: a string containing 'E', 'W', 'N', or 'S'
    :return: a string containing 'E', 'W', 'N', or 'S'
    """
    if direction == 'E':
        return 'W'
    elif direction == 'W':
        return 'E'
    elif direction == 'N':
        return 'S'
    elif direction == 'S':
        return 'N'
    else:
        raise ValueError('Invalid or unsupported direction {} given.'.format(direction))


def point(data: str):
    """
    Find the lon & lat of a line of record.
    :param data:
    :return:
    """
    lat = data.split(',')[4]
    lon = data.split(',')[5]
    # return ev.LatLon(point_n, point_w)
    if lon[-1] in ['E', 'W']:
        lon_num = float(lon[:-1])
        lon_dir = lon[-1]
    else:
        lon_num = float(lon)
    if lon_num > 180.0:  # Does longitude exceed range?
        lon_num = 360.0 - lon_num
        lon_dir = flip_direction(lon_dir)
        lon = str(lon_num) + lon_dir

    return ev.LatLon(lat, lon)


def storm_date(record: str):
    """
    Find the date of one record.
    :param record: one line of record.
    :return: the date of the record.
    """
    return record.split(',')[0].strip()


def storm_time(record: str):
    """
    Find the time of the record.
    :param record: one line of record.
    :return: the time of the record.
    """
    return record.split(',')[1].strip()


def hour_diff(time1: str, time2: str) ->float:
    """
    Calculate the difference of two time, formatting %Y%m%d%H%M.
    :param time1: The first time string
    :param time2: The second time string
    :return: The hours difference between two time
    """
    s1 = datetime.datetime.strptime(time1, "%Y%m%d%H%M")
    s2 = datetime.datetime.strptime(time2, "%Y%m%d%H%M")
    return abs(s2-s1).seconds / 3600.0

def norm(angle):
    if angle > 360:
        return angle - 360
    else:
        return angle

def check(indices: list, bearing: float):
    """
    Determine if a storm bearing on the direction as the hypothesis based on my understanding.
    :param indices: a list of integer indicate index of which radii is the max
    :param bearing: the direction the storm is heading
    :return: Return 1 if the bearing is in the quadrant. Else return None.
    """
    # transfer bearing to index of the quadrant
    # 0 for northeastern, 1 for southeastern, 2 for southwestern, 3 for northwestern
    min_bearing = int(norm(bearing + 45)/90)
    max_bearing = int(norm(bearing + 90)/90)
    indices1 = []

    if 0 in indices or 4 in indices or 8 in indices:  # Northeastern
        indices1.append(0)
    if 1 in indices or 5 in indices or 9 in indices:  # Southeastern
        indices1.append(1)
    if 2 in indices or 6 in indices or 10 in indices:  # Southwestern
        indices1.append(2)
    if 3 in indices or 7 in indices or 11 in indices:  # Northwestern
        indices1.append(3)

    if min_bearing in indices1 or max_bearing in indices1:
        return 1
    else:
        return None


def main():
    with open('hurdat2-1851-2016-041117.csv','r') as file:  # for different file, change path here
    # with open('hurdat2-nepac-1949-2016-041317.csv.txt') as file:
        row = file.readline()
        year = []
        hurricane = []
        result = []
        while row:
            if row[0].isalpha():  # this line is the name and id of the storm
                print('Storm System ID: ', storm_id(row))
                if storm_name(row):
                    print('Storm System Name: ', storm_name(row))
                date = []
                h = []
                max_wind = 0
                count = 0
                d = 0
                t = 0
                row = file.readline()  # go into the record
                y = year_of(row)
                year.append(y)
                curr_point = point(row)
                curr_time = storm_date(row) + storm_time(row)
                sum_distance = 0
                storm_propagation = []
                while row[0].isdigit():
                    if row.split(',')[0].strip()[0].isdigit():
                        date.append(row.split(',')[0].strip())
                        radii = row.split(',')[8:]
                        if wind(row) > max_wind:
                            max_wind = wind(row)
                            d = storm_date(row)
                            t = storm_time(row)
                        if is_landfill(row):
                            count += 1
                        if is_hurricane(row):
                            h.append(year_of(row))
                    row = file.readline()
                    if row == '':  # end of the file
                        break
                    if row[0].isalpha():
                        break
                    next_point = point(row)
                    next_time = storm_date(row) + storm_time(row)
                    if curr_point != next_point:
                        distance = curr_point.distanceTo(next_point) / 1852.0
                        bearing = curr_point.bearingTo(next_point)
                    else:
                        distance = 0
                        bearing = 0
                    sum_distance += distance
                    storm_propagation.append(distance / hour_diff(curr_time,next_time))
                    # ignore the record if the record is missed or the storm is not strong enough or the storm is not moving and marked as -1
                    if int(max(radii)) == -999 or int(max(radii)) == 0 or bearing == 0:
                        result.append(-1)
                    else:
                        indices = [i for i, x in enumerate(radii) if x == max(radii)]  # record the index of all max level radii
                        result.append(check(indices, bearing))
                    curr_point = next_point
                    curr_time = next_time
                print('Landfall: ', count)
                print('Highest Maximum sustained wind (in knots):', max_wind, ' Date:', d, 'Time:', t)
                print('Start: ', date[0])
                if len(date) > 1:
                    print('End: ', date[-1])
                else:
                    print('End: ', date[0])
                if h:
                    hurricane.append(y)
                print('Total Distance: {:.2f}'.format(sum_distance))
                if storm_propagation:
                    if not len(storm_propagation) == 1:
                        max_speed = max(storm_propagation)
                        mean_speed = sum(storm_propagation) / float(len(storm_propagation))
                    else:
                        max_speed = storm_propagation[0]
                        mean_speed = max_speed
                    print('Maximum propagation speeds: {:.4f}'.format(max(storm_propagation)))
                    print('Mean propagation speeds: {:.4f}'.format(mean_speed))
                else:
                    print('Maximum propagation speeds: 0')
                    print('Mean propagation speeds: 0')
                print()
                continue
            row = file.readline()

        print('--------------------SUMMARY--------------------')
        c = Counter(year)
        c1 = Counter(hurricane)
        start_year = year[0]
        while start_year <= year[-1]:
            print("Total number of storms tracked in", start_year, ':', c[start_year])
            print('Total number of hurricanes tracked in', start_year, ':', c1[start_year])
            print()
            start_year += 1
        print('------------------------------------------------')
        c3 = Counter(result)
        rate = (c3[1]/(c3[1]+c3[None])) * 100.0
        print('{:.2f}% of the the time the hypothesis was true.'.format(rate))


if __name__ == '__main__':
    main()


