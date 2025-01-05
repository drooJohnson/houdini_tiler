Throw this script on a button, or in the Python Source Editor and run to split your render into tiles.
The xtiles/ytiles parameters of the tile_camera function will change the number of tiles.

If you want to use the timestamp functionality included in the tiler without the tiling, just add the following to the "Common File Prefix" in your redshift ROP:
``pythonexprs("str(__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S'))")``

For example, if you want to timestamp to be just after the project's name and the ROP's name in the output file:
`$HIP/render/$HIPNAME.$OS.`pythonexprs("str(__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S'))")`.$F4.exr`
