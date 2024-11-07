import numpy as np
from math import sin, cos, radians, sqrt
import numbers

class Quaternion:
    def __init__(self, s, x=None, y=None, z=None):
        # Quaternion initialization
        if x is not None and y is not None and z is not None:
            w = s
            self._q = np.array([w, x, y, z])
        elif isinstance(s, Quaternion):
            self._q = np.array(s._q)
        else:
            self._q = np.array(s)
            if len(self._q) != 4:
                raise ValueError("Expecting an array of 4 elements or w x y z as parameters")

    def conjugate(self):
        # Quaternion conjugate
        return Quaternion(self._q[0], -self._q[1], -self._q[2], -self._q[3])

    def norm(self):
        # Quaternion norm
        return sqrt(np.sum(self._q ** 2))

    def __mul__(self, other):
        # Multiplying a quaternion by a quaternion or scalar
        if isinstance(other, Quaternion):
            w = self._q[0] * other._q[0] - np.dot(self._q[1:], other._q[1:])
            xyz = np.cross(self._q[1:], other._q[1:]) + self._q[0] * other._q[1:] + other._q[0] * self._q[1:]
            return Quaternion(w, *xyz)
        elif isinstance(other, numbers.Number):
            return Quaternion(self._q * other)

    def __add__(self, other):
        # Quaternion addition
        if isinstance(other, Quaternion):
            return Quaternion(self._q + other._q)
        elif isinstance(other, (list, tuple, np.ndarray)) and len(other) == 4:
            return Quaternion(self._q + np.array(other))
        else:
            raise TypeError("Expecting an array of 4 elements or another Quaternion")

    @staticmethod
    def euler_to_quat(roll, pitch, yaw):
        # Converting Euler angles to quaternions
        roll_rad, pitch_rad, yaw_rad = radians(roll), radians(pitch), radians(yaw)

        cy, sy = cos(yaw_rad / 2), sin(yaw_rad / 2)
        cp, sp = cos(pitch_rad / 2), sin(pitch_rad / 2)
        cr, sr = cos(roll_rad / 2), sin(roll_rad / 2)

        w = cr * cp * cy + sr * sp * sy
        x = sr * cp * cy - cr * sp * sy
        y = cr * sp * cy + sr * cp * sy
        z = cr * cp * sy - sr * sp * cy

        return Quaternion(w, x, y, z)

    def rotate_vector(self, vector):
        # Rotation of one vector via quaternion
        vector_q = Quaternion(0, *vector)
        rotated_q = self * vector_q * self.conjugate()
        return rotated_q._q[1:]  # Возвращаем только мнимую часть (3D вектор)

    @staticmethod
    def rotate_space_euler(roll, pitch, yaw, vectors):
        # Creating a quaternion from Euler angles
        rotation_quaternion = Quaternion.euler_to_quat(roll, pitch, yaw)

        # Apply rotation to each vector
        return [rotation_quaternion.rotate_vector(v) for v in vectors]


    def __repr__(self):
        return f'Quaternion({self._q[0]:.4f}, {self._q[1]:.4f}, {self._q[2]:.4f}, {self._q[3]:.4f})'

if __name__ == '__main__':
    q1 = Quaternion(1, 0, 0, 0)
    print("q1:", q1)

    q2 = Quaternion([0.707, 0.707, 0, 0])
    print("q2:", q2)

    q3 = Quaternion(q2)
    print("q3 (duplicate q2):", q3)

    q4 = q1 * q2
    print("Product q1 и q2:", q4)

    q5 = q1 + q2
    print("Sum q1 and q2:", q5)

    scalar_multiplied_q = q2 * 2
    print("q2 multiplied by scalar 2:", scalar_multiplied_q)

    q1_conj = q1.conjugate()
    print("Quaternion conjugate q1:", q1_conj)

    # Converting Euler angles to quaternions
    euler_quat = Quaternion.euler_to_quat(30, 45, 60)
    print("Quaternion from Euler angles (30, 45, 60 degrees):", euler_quat)

    # Rotate a vector using a quaternion
    vector = [0, 1, 0]
    rotated_vector = euler_quat.rotate_vector(vector)
    print("Source vector:", vector)
    print("Rotated vector using quaternion:", rotated_vector)

    vectors = [
        [1, 0, 0],  # Along the X-axis
        [0, 1, 0],  # Along the Y-axis
        [0, 0, 1]   # Along the Z-axis
    ]
    roll, pitch, yaw = 30, 45, 60

    rotated_vectors = Quaternion.rotate_space_euler(roll, pitch, yaw, vectors)
    print("Original vectors:", vectors)
    for i, vec in enumerate(rotated_vectors):
        print(f"Rotated vector {i+1}: {vec}")
