import helper
import unittest


class TestAll(unittest.TestCase):
  def test_task_distribution(self):
      self.assertTupleEqual(helper.distribute_tasks_per_processes(10, 1), ((0, 9),))
      self.assertTupleEqual(helper.distribute_tasks_per_processes(10, 2), ((0, 4), (5, 9)))
      self.assertTupleEqual(helper.distribute_tasks_per_processes(10, 3), ((0, 3), (4, 7), (8, 9)))
      self.assertTupleEqual(helper.distribute_tasks_per_processes(2, 4), ((0, 0), (1, 1), None, None))

if __name__ == '__main__':
    unittest.main()