from utils.primitives import Matrix


def transpose(matrix: Matrix):
    return Matrix(matrix.columns())