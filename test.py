def thirdMax(nums: list[int]) -> int:
    if len(nums) < 3:
        return max(nums)

    mx_1 = -float('inf') + 2
    mx_2 = -float('inf') + 1
    mx_3 = -float('inf')

    for num in nums:
        if num > mx_1:
            mx_1, mx_2, mx_3 = num, mx_1, mx_2
        elif num > mx_2:
            mx_2, mx_3 = num, mx_2
        elif num > mx_3:
            mx_3 = num

    return mx_3


nums = [2, 2, 3, 1]

thirdMax(nums)
