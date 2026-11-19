import json
import os
import xbmc
import xbmcvfs
from logger import *


OLD_ADDON_ID = 'plugin.video.rokuchannel'
NEW_ADDON_ID = 'metalchris.rokuchannel.video'


def migrate_old_addon_data():
    """
    Migrate userdata from the old Roku Channel add-on ID to the new ID.

    The old add-on is disabled only after the userdata migration succeeds.
    """

    old_path = xbmcvfs.translatePath(
        f'special://profile/addon_data/{OLD_ADDON_ID}/'
    )
    new_path = xbmcvfs.translatePath(
        f'special://profile/addon_data/{NEW_ADDON_ID}/'
    )

    old_exists = xbmcvfs.exists(old_path)
    new_exists = xbmcvfs.exists(new_path)

    log(f'[MIGRATION] Old userdata exists: {old_exists}', xbmc.LOGINFO)
    log(f'[MIGRATION] New userdata exists: {new_exists}', xbmc.LOGINFO)

    # Nothing to migrate.
    if not old_exists:
        log('[MIGRATION] Old userdata not found', xbmc.LOGINFO)
        return True

    # Don't risk overwriting existing new userdata.
    if new_exists:
        log(
            '[MIGRATION] Both old and new userdata directories exist. '
            'Migration skipped.',
            xbmc.LOGWARNING
        )
        return False

    # Create the new userdata directory.
    if not xbmcvfs.mkdirs(new_path):
        log(
            f'[MIGRATION] Failed to create new userdata directory: {new_path}',
            xbmc.LOGERROR
        )
        return False

    # Copy the contents of the old userdata directory.
    dirs, files = xbmcvfs.listdir(old_path)

    for filename in files:
        source = os.path.join(old_path, filename)
        destination = os.path.join(new_path, filename)

        if not xbmcvfs.copy(source, destination):
            log(
                f'[MIGRATION] Failed to copy: {filename}',
                xbmc.LOGERROR
            )
            return False

        log(
            f'[MIGRATION] Copied: {filename}',
            xbmc.LOGDEBUG
        )

    # The current userdata directory contains files rather than
    # subdirectories, but handle directories too so future files/folders
    # don't get silently ignored.
    for dirname in dirs:
        source = os.path.join(old_path, dirname)
        destination = os.path.join(new_path, dirname)

        if not xbmcvfs.mkdirs(destination):
            log(
                f'[MIGRATION] Failed to create directory: {dirname}',
                xbmc.LOGERROR
            )
            return False

        if not copy_directory(source, destination):
            return False

    # Verify that everything from the old directory exists in the new one.
    if not verify_migration(old_path, new_path):
        log(
            '[MIGRATION] Verification failed. Old add-on will remain enabled.',
            xbmc.LOGERROR
        )
        return False

    log('[MIGRATION] Userdata migration successful', xbmc.LOGINFO)

    # Only disable the old add-on after migration has been verified.
    if disable_old_addon():
        log(
            f'[MIGRATION] Disabled old add-on: {OLD_ADDON_ID}',
            xbmc.LOGINFO
        )
    else:
        log(
            f'[MIGRATION] Failed to disable old add-on: {OLD_ADDON_ID}',
            xbmc.LOGERROR
        )

    return True


def copy_directory(source, destination):
    """Recursively copy a directory using xbmcvfs."""

    dirs, files = xbmcvfs.listdir(source)

    for filename in files:
        source_file = os.path.join(source, filename)
        destination_file = os.path.join(destination, filename)

        if not xbmcvfs.copy(source_file, destination_file):
            log(
                f'[MIGRATION] Failed to copy: {source_file}',
                xbmc.LOGERROR
            )
            return False

    for dirname in dirs:
        source_dir = os.path.join(source, dirname)
        destination_dir = os.path.join(destination, dirname)

        if not xbmcvfs.mkdirs(destination_dir):
            log(
                f'[MIGRATION] Failed to create directory: {destination_dir}',
                xbmc.LOGERROR
            )
            return False

        if not copy_directory(source_dir, destination_dir):
            return False

    return True


def verify_migration(old_path, new_path):
    """Verify that all old userdata files and directories exist in the new location."""

    dirs, files = xbmcvfs.listdir(old_path)

    for filename in files:
        if not xbmcvfs.exists(os.path.join(new_path, filename)):
            log(
                f'[MIGRATION] Missing copied file: {filename}',
                xbmc.LOGERROR
            )
            return False

    for dirname in dirs:
        source_dir = os.path.join(old_path, dirname)
        destination_dir = os.path.join(new_path, dirname)

        if not xbmcvfs.exists(destination_dir):
            log(
                f'[MIGRATION] Missing copied directory: {dirname}',
                xbmc.LOGERROR
            )
            return False

        if not verify_migration(source_dir, destination_dir):
            return False

    return True


def disable_old_addon():
    """Disable the old Roku Channel add-on through Kodi's JSON-RPC API."""

    request = {
        'jsonrpc': '2.0',
        'method': 'Addons.SetAddonEnabled',
        'params': {
            'addonid': OLD_ADDON_ID,
            'enabled': False
        },
        'id': 1
    }

    try:
        response = xbmc.executeJSONRPC(json.dumps(request))
        result = json.loads(response)

        if 'error' in result:
            log(
                f'[MIGRATION] Disable failed: {result["error"]}',
                xbmc.LOGERROR
            )
            return False

        return result.get('result') == 'OK'

    except Exception as exc:
        log(
            f'[MIGRATION] Exception disabling old add-on: {exc}',
            xbmc.LOGERROR
        )
        return False
