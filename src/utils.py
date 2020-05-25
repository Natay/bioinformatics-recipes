import pandas as pd


def alias(df, fname, key1='col1', key2='col2', name='foo', delimiter='\t'):
    """
    Replaces the column named "dest" of an existing dataframe
    with the column named "target" of a file for all position
    of where the column named "source" of the new file matches
    the the value in "dest"

    """

    try:

        # Read a table into a dataframe.
        frame = pd.read_table(fname, delimiter=delimiter)

        # Create a mapping of key2 to a new column value
        remap = dict(zip(frame[key2], frame[name]))

        # Remap the existing values if possible.
        values = [remap.get(v, v) for v in df[key1]]

        # Assign the new values to the dataframe.
        df[key1] = values

    except Exception as exc:
        # Gets in the way when this gets pipelined to a file
        #print(f"Aliasing not performed: {exc}")
        pass

    return df

def get_subset(df, rank=''):
    indices = df['rank'] == rank
    subset = df[indices] if rank else df
    return subset