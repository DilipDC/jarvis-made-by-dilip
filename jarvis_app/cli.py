from __future__ import annotations
import argparse, json
from .core.app import agent

def main():
    p=argparse.ArgumentParser(prog='jarvis'); sub=p.add_subparsers(dest='cmd')
    sub.add_parser('status'); sub.add_parser('doctor'); chat=sub.add_parser('chat'); chat.add_argument('text',nargs='+')
    args=p.parse_args()
    if args.cmd=='status': print(json.dumps(agent.status(),indent=2,default=str)); return
    if args.cmd=='doctor':
        s=agent.status(); checks={'python':'PASS','sqlite':'PASS' if s['memory']['available'] else 'FAIL','ollama':'PASS' if s['model']['available'] else 'WARN','browser':'PASS' if s['browser']['available'] else 'WARN','mcp':'PASS' if s['mcp'].get('available') else 'WARN','voice':'PASS' if (s['voice'].get('stt') or s['voice'].get('tts')) else 'WARN'}; print(json.dumps({'status':'PASS' if 'FAIL' not in checks.values() else 'FAIL','checks':checks},indent=2)); return
    if args.cmd=='chat': print(agent.chat(' '.join(args.text)).get('text','')); return
    p.print_help()
if __name__=='__main__': main()
