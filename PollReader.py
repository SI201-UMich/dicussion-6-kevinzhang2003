import os
import unittest


class PollReader():
    """
    A class for reading and analyzing polling data.
    """
    def __init__(self, filename):
        """
        The constructor. Opens up the specified file, reads in the data,
        closes the file handler, and sets up the data dictionary that will be
        populated with build_data_dict().

        We have implemented this for you. You should not need to modify it.
        """

        # this is used to get the base path that this Python file is in in an
        # OS agnostic way since Windows and Mac/Linux use different formats
        # for file paths, the os library allows us to write code that works
        # well on any operating system
        self.base_path = os.path.abspath(os.path.dirname(__file__))

        # join the base path with the passed filename
        self.full_path = os.path.join(self.base_path, filename)

        # open up the file handler
        self.file_obj = open(self.full_path, 'r')

        # read in each line of the file to a list
        self.raw_data = self.file_obj.readlines()

        # close the file handler
        self.file_obj.close()

        # set up the data dict that we will fill in later
        self.data_dict = {
            'month': [],
            'date': [],
            'sample': [],
            'sample type': [],
            'Harris result': [],
            'Trump result': []
        }

    def build_data_dict(self):
        """
        Reads all of the raw data from the CSV and builds a dictionary where
        each key is the name of a column in the CSV, and each value is a list
        containing the data for each row under that column heading.

        There may be a couple bugs in this that you will need to fix.
        Remember that the first row of a CSV contains all of the column names,
        and each value in a CSV is seperated by a comma.
        """

        # Reset the dictionary in case this is called again
        self.data_dict = {
            'month': [],
            'date': [],
            'sample': [],
            'sample type': [],
            'Harris result': [],
            'Trump result': []
        }

        if len(self.raw_data) == 0:
            return

        # Loop through lines. Skip header (first line).
        for idx in range(len(self.raw_data)):
            line = self.raw_data[idx].strip()
            if line == "":
                continue
            if idx == 0:
                # header line
                continue

            parts = line.split(',')
            # Expecting 5 columns: month, date, sample, Harris result, Trump result
            if len(parts) < 5:
                continue

            month = parts[0]
            date_str = parts[1]
            sample_field = parts[2]
            harris_str = parts[3]
            trump_str = parts[4]

            # sample looks like "1880 LV" -> size and type
            sample_parts = sample_field.split()
            if len(sample_parts) >= 2:
                sample_size_str = sample_parts[0]
                sample_type = sample_parts[1]
            else:
                sample_size_str = sample_parts[0]
                sample_type = ""

            # Append with correct types
            self.data_dict['month'].append(month)
            self.data_dict['date'].append(int(date_str))
            self.data_dict['sample'].append(int(sample_size_str))
            self.data_dict['sample type'].append(sample_type)
            self.data_dict['Harris result'].append(float(harris_str))
            self.data_dict['Trump result'].append(float(trump_str))

    def highest_polling_candidate(self):
        """
        This method should iterate through the result columns and return
        the name of the candidate with the highest single polling percentage
        alongside the highest single polling percentage.
        If equal, return the highest single polling percentage and "EVEN".

        Returns:
            str: A string indicating the candidate with the highest polling percentage or EVEN,
             and the highest polling percentage.
        """
        if len(self.data_dict['Harris result']) == 0 or len(self.data_dict['Trump result']) == 0:
            return "EVEN 0.0%"

        # Find maximums using simple loops
        h_max = 0.0
        for v in self.data_dict['Harris result']:
            if v > h_max:
                h_max = v

        t_max = 0.0
        for v in self.data_dict['Trump result']:
            if v > t_max:
                t_max = v

        if h_max == t_max:
            return "EVEN " + f"{h_max:.1%}"
        elif h_max > t_max:
            return "Harris " + f"{h_max:.1%}"
        else:
            return "Trump " + f"{t_max:.1%}"


    def likely_voter_polling_average(self):
        """
        Calculate the average polling percentage for each candidate among likely voters.

        Returns:
            tuple: A tuple containing the average polling percentages for Harris and Trump
                   among likely voters, in that order.
        """
        h_total = 0.0
        t_total = 0.0
        count = 0

        # Iterate by index to match rows
        i = 0
        while i < len(self.data_dict['sample type']):
            if self.data_dict['sample type'][i] == "LV":
                h_total = h_total + self.data_dict['Harris result'][i]
                t_total = t_total + self.data_dict['Trump result'][i]
                count = count + 1
            i = i + 1

        if count == 0:
            return (0.0, 0.0)

        h_avg = h_total / count
        t_avg = t_total / count
        return (h_avg, t_avg)


    def polling_history_change(self):
        """
        Calculate the change in polling averages between the earliest and latest polls.

        This method calculates the average result for each candidate in the earliest 30 polls
        and the latest 30 polls, then returns the net change.

        Returns:
            tuple: A tuple containing the net change for Harris and Trump, in that order.
                   Positive values indicate an increase, negative values indicate a decrease.
        """
        n = len(self.data_dict['Harris result'])
        if n == 0:
            return (0.0, 0.0)

        # Use up to 30 polls on each side
        k = 30
        if n < 30:
            k = n

        # Latest polls are at the top of the file (first rows after header)
        # Indices: 0..k-1
        h_latest_total = 0.0
        t_latest_total = 0.0
        i = 0
        while i < k:
            h_latest_total = h_latest_total + self.data_dict['Harris result'][i]
            t_latest_total = t_latest_total + self.data_dict['Trump result'][i]
            i = i + 1

        # Earliest polls are at the bottom of the file (last rows)
        # Indices: n-k..n-1
        h_earliest_total = 0.0
        t_earliest_total = 0.0
        j = n - k
        while j < n:
            h_earliest_total = h_earliest_total + self.data_dict['Harris result'][j]
            t_earliest_total = t_earliest_total + self.data_dict['Trump result'][j]
            j = j + 1

        h_latest_avg = h_latest_total / k
        t_latest_avg = t_latest_total / k
        h_earliest_avg = h_earliest_total / k
        t_earliest_avg = t_earliest_total / k

        return (h_latest_avg - h_earliest_avg, t_latest_avg - t_earliest_avg)


class TestPollReader(unittest.TestCase):
    """
    Test cases for the PollReader class.
    """
    def setUp(self):
        self.poll_reader = PollReader('polling_data.csv')
        self.poll_reader.build_data_dict()

    def test_build_data_dict(self):
        self.assertEqual(len(self.poll_reader.data_dict['date']), len(self.poll_reader.data_dict['sample']))
        self.assertTrue(all(isinstance(x, int) for x in self.poll_reader.data_dict['date']))
        self.assertTrue(all(isinstance(x, int) for x in self.poll_reader.data_dict['sample']))
        self.assertTrue(all(isinstance(x, str) for x in self.poll_reader.data_dict['sample type']))
        self.assertTrue(all(isinstance(x, float) for x in self.poll_reader.data_dict['Harris result']))
        self.assertTrue(all(isinstance(x, float) for x in self.poll_reader.data_dict['Trump result']))

    def test_highest_polling_candidate(self):
        result = self.poll_reader.highest_polling_candidate()
        self.assertTrue(isinstance(result, str))
        self.assertTrue("Harris" in result)
        self.assertTrue("57.0%" in result)

    def test_likely_voter_polling_average(self):
        harris_avg, trump_avg = self.poll_reader.likely_voter_polling_average()
        self.assertTrue(isinstance(harris_avg, float))
        self.assertTrue(isinstance(trump_avg, float))
        self.assertTrue(f"{harris_avg:.2%}" == "49.34%")
        self.assertTrue(f"{trump_avg:.2%}" == "46.04%")

    def test_polling_history_change(self):
        harris_change, trump_change = self.poll_reader.polling_history_change()
        self.assertTrue(isinstance(harris_change, float))
        self.assertTrue(isinstance(trump_change, float))
        self.assertTrue(f"{harris_change:+.2%}" == "+1.53%")
        self.assertTrue(f"{trump_change:+.2%}" == "+2.07%")


def main():
    poll_reader = PollReader('polling_data.csv')
    poll_reader.build_data_dict()

    highest_polling = poll_reader.highest_polling_candidate()
    print(f"Highest Polling Candidate: {highest_polling}")
    
    harris_avg, trump_avg = poll_reader.likely_voter_polling_average()
    print(f"Likely Voter Polling Average:")
    print(f"  Harris: {harris_avg:.2%}")
    print(f"  Trump: {trump_avg:.2%}")
    
    harris_change, trump_change = poll_reader.polling_history_change()
    print(f"Polling History Change:")
    print(f"  Harris: {harris_change:+.2%}")
    print(f"  Trump: {trump_change:+.2%}")



if __name__ == '__main__':
    main()
    unittest.main(verbosity=2)