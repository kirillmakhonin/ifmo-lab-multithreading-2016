import helper, calculator
import unittest


class TestAll(unittest.TestCase):
    # def test_task_distribution(self):
    #     data = [1, 123, 124, 10, 2, 40, 50, 100]
    #     print(data)
    #     calculator.quicksort(data, 0, len(data) - 1)
    #     print(data)

    def test_get_super_cubes(self):
        step3 = set([0])
        step2 = set([0, 4])
        step1 = set([0, 2, 4, 6])
        self.assertSetEqual(step1, set(helper.get_super_cubes(3, 1)))
        self.assertSetEqual(step3, set(helper.get_super_cubes(3, 3)))
        self.assertSetEqual(step2, set(helper.get_super_cubes(3, 2)))

    def test_get_super_cube(self):
        self.assertEqual(0, helper.get_my_super_cube(3, 1))
        self.assertEqual(0, helper.get_my_super_cube(3, 2))
        self.assertEqual(0, helper.get_my_super_cube(3, 3))
        self.assertEqual(0, helper.get_my_super_cube(3, 4))
        self.assertEqual(0, helper.get_my_super_cube(3, 5))
        self.assertEqual(0, helper.get_my_super_cube(3, 6))
        self.assertEqual(0, helper.get_my_super_cube(3, 7))
        self.assertEqual(0, helper.get_my_super_cube(2, 1))
        self.assertEqual(0, helper.get_my_super_cube(2, 2))
        self.assertEqual(0, helper.get_my_super_cube(2, 3))
        self.assertEqual(4, helper.get_my_super_cube(2, 5))
        self.assertEqual(4, helper.get_my_super_cube(2, 6))
        self.assertEqual(4, helper.get_my_super_cube(2, 7))
        self.assertEqual(0, helper.get_my_super_cube(1, 1))
        self.assertEqual(2, helper.get_my_super_cube(1, 3))
        self.assertEqual(4, helper.get_my_super_cube(1, 5))
        self.assertEqual(6, helper.get_my_super_cube(1, 7))

    def test_quicksort(self):
        test_matrix = (
            ([0, 1, 2, 3, 4], 2, [0, 1, 2, 3, 4], 2),
            ([4, 3, 2, 1, 0], 2, [0, 1, 2, 3, 4], 2),
            ([3, 4, 2, 0, 1], 2, [1, 0, 2, 4, 3], 2),
            ([1, 2, 11, 3, 4, 12, 5, 16], 10, [1, 2, 5, 3, 4, 12, 11, 16], 5),
            ([1, 2, 11, 12, 13, 3, 14, 4, 15], 10, [1, 2, 4, 3, 13, 12, 14, 11, 15], 4),
            ([24, 84], 84, [24, 84], 1),
            ([55, 81], 84, [55, 81], 2),
            ([40, 149], 84, [40, 149], 1),
            ([86, 97], 84, [86, 97], 0),
        )

        for test, (src, pivot, expected_result, expected_pos) in enumerate(test_matrix):
            expected = sorted(src)
            helper.quicksort(src)
            self.assertListEqual(src, expected, msg="Error on line %d" % test)

    def test_list_split(self):
        test_matrix = (
            ([0, 1, 2, 3, 4], 2, [0, 1, 2, 3, 4], 2),
            ([4, 3, 2, 1, 0], 2, [0, 1, 2, 3, 4], 2),
            ([3, 4, 2, 0, 1], 2, [1, 0, 2, 4, 3], 2),
            ([1, 2, 11, 3, 4, 12, 5, 16], 10, [1, 2, 5, 3, 4, 12, 11, 16], 5),
            ([1, 2, 11, 12, 13, 3, 14, 4, 15], 10, [1, 2, 4, 3, 13, 12, 14, 11, 15], 4),
            ([24, 84], 84, [24, 84], 1),
            ([55, 81], 84, [55, 81], 2),
            ([40, 149], 84, [40, 149], 1),
            ([86, 97], 84, [86, 97], 0),
        )

        for test, (src, pivot, expected_result, expected_pos) in enumerate(test_matrix):
            pos = helper.split_list(pivot, src)
            self.assertListEqual(src, expected_result, msg="Error on line %d" % test)
            self.assertEqual(pos, expected_pos, msg="Error on line %d" % test)

    def test_my_childs(self):
        test_matrix = (
            ((1, 0), (1,)),
            ((1, 4), (5,)),
            ((2, 0), (1, 2, 3)),
            ((2, 4), (5, 6, 7)),
            ((3, 0), (1, 2, 3, 4, 5, 6, 7)),
        )

        for (iteration, rank), excepted_result in test_matrix:
            childs = set(helper.get_my_childs(iteration, rank))
            self.assertSetEqual(set(excepted_result), childs)

    def test_get_neighbor(self):
        test_matrix = (
            (3, 0, 4, False),
            (3, 4, 0, True),
            (1, 0, 1, False),
            (1, 6, 7, False),
            (1, 7, 6, True),
        )
        for iter, current, neighbor, send_low in test_matrix:
            self.assertTupleEqual((neighbor, send_low), helper.get_my_neighbor_should_send_low(iter, current))


if __name__ == '__main__':
    unittest.main()
