# -*- mode: python -*-

block_cipher = None


a = Analysis(['battle.py'],
             pathex=['D:\\files\\programers_files\\Projects\\ROOTBOT', 'D:\\files\\programers_files\\Projects\\ROOTBOT\\T_bot'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='battle',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
