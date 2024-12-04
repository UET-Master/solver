float getAverage(int arr[], int n) {
    float avg = 0;
    int temp = 0;

    if (n > 0) {
        for (int i = 0; i < n; i++) {
            temp += arr[i];
        }
        avg = temp / n;
    }

    return avg;
}