


def progress_bar(current, total, bar_len = 20):
    """
    Function to print a progress bar.
    """
    percent = float(current) / total
    arrow = '-' * int(percent * bar_len - 1) + '>'
    spaces  = ' ' * (bar_len - len(arrow))
    print('Progress: [{}{}] {}/{}'.format(arrow, spaces, current, total), end='\r')