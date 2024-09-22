
    try:
        async with aiofiles.open(file_path, 'wb') as file:
            while contents := await in_file.read(FILE_CHUNK_SIZE):
                await file.write(contents)
    except Exception as e:
        raise HTTPException(
            detail={'message': f'Error during file uploading: {str(e)}'},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    finally:
        await file.close()