using System;
using System.Text;
using System.Linq;
using System.Diagnostics;
using System.Collections.Generic;
public class LogUtils {
    //前端空白拼接的缓存
	public static List<StringBuilder> stackIndentList = new List<StringBuilder> ();
	//实际LOG的缓存
	public static List<StringBuilder> _stackLogCacheList = new List<StringBuilder> ();
	//类方法名的缓存
	public static List<StringBuilder> _stackClassMethodCacheList = new List<StringBuilder> ();
	public static List<string> filterList =  new List<string> ();
	//Log输出中
	public static bool logging = true;
	//达到多少才输出
	public static int logOutputCount = 1;
	public static bool fullMethodName = false;
	public static int lastStackFrameLength = 0;
	public static string logPath = "/Volumes/Files/develop/selfDevelop/Unity/Flash2Unity2018/C#Temp/C#Log";
	//切开字符串
	public static string[] splitAWithB (string a_, string b_) {
		Char[] _bChars = b_.ToCharArray ();
		string[] _aList = a_.Split (_bChars);
		return _aList;
	}
	//包含判断
	public static bool isAContainsB (string a_, string b_, StringComparison comp_ = StringComparison.OrdinalIgnoreCase) {
		return a_.IndexOf (b_, comp_) >= 0;
	}
    // 调用方式
    // LogUtils.FuncIn(System.Reflection.MethodBase.GetCurrentMethod().ReflectedType.FullName);
	public static void FuncIn(string className_,string parameters_ = ""){
		if (logging == false){
			return;
		}
		if (filterList.Count == 0){
			filterList.Add("OtherUtils -> getFloat");
			filterList.Add("OtherUtils -> cacheFrameInfo");
			filterList.Add("OtherUtils -> propertyToList");
			filterList.Add("OtherUtils -> setTo");
		}

		StackTrace _stackTrace = new System.Diagnostics.StackTrace();
		int _stackFrameLength = _stackTrace.FrameCount;
		bool _stackBeginBool = false;
		//当前长度2，且小于等于上一次记录的长度，证明回归第一层
		if (_stackFrameLength == 2 && _stackFrameLength <= lastStackFrameLength){
			_stackBeginBool = true;//新起的一个堆栈起点
		}
		while (stackIndentList.Count < _stackFrameLength){
			StringBuilder _stackBlankPrefix =  new StringBuilder ();
            _stackBlankPrefix.Append ("->");
			for (int _idx = 0; _idx < _stackFrameLength; _idx++){
                _stackBlankPrefix.Append ("    ");
			}
			stackIndentList.Add(_stackBlankPrefix);
		} 
		StackFrame _stackFrame = _stackTrace.GetFrame(1);
		string _methodName;//当前方法名
		if (fullMethodName){//要全称，带函数签名
			_methodName = _stackFrame.GetMethod().ToString();
		}else{//只要方法名
			_methodName = _stackFrame.GetMethod().Name;
		}
		string _className = className_;
		string[] _classNameArr;
		if (isAContainsB(_className,"+")){
			_classNameArr = splitAWithB(_className,"+");
			_className = _classNameArr[_classNameArr.Length - 1];
		}else if (isAContainsB(_className,".")){
			_classNameArr = splitAWithB(_className,".");
			_className = _classNameArr[_classNameArr.Length - 1];
		}

		StringBuilder _classAndMethod = new StringBuilder ();//拼接类方法
        _classAndMethod.Append (_className);
        _classAndMethod.Append (" -> ");
        _classAndMethod.Append (_methodName);

		string _classAndMethodStr = _classAndMethod.ToString();
		for(int _idx = 0;_idx < filterList.Count; _idx++){
			if (filterList[_idx] == _classAndMethodStr){
				return;
			}
		}

		_stackClassMethodCacheList.Add(_classAndMethod);//记录 类->方法
		StringBuilder _log = new StringBuilder ();
		if (_stackBeginBool){
			_log.Append ("----->");//拼接前端空白
		}else{
			_log.Append (stackIndentList[ _stackFrameLength - 1]);//拼接前端空白
		}
		
		_log.Append (_classAndMethod);//拼接 类 -> 方法
		if (parameters_ != ""){
			_log.Append(parameters_);
		}
		_stackLogCacheList.Add(_log);//缓存Log
		if(_stackLogCacheList.Count >= logOutputCount){//当缓存大于指定数值
			StringBuilder _logCache = new StringBuilder();//log缓存的拼接
			for (int _idx = 0; _idx < logOutputCount; _idx++){
				StringBuilder _tempLog = _stackLogCacheList[_idx];//当前Log
				_tempLog.Append ("\n");//每个Log间添加换行
				_logCache.Append(_tempLog);	//拼接
			}
			_stackClassMethodCacheList.Clear();//清理缓存
			_stackLogCacheList.Clear();//清理Log
			string _logCacheStr = _logCache.ToString();//转换成字符串
			System.IO.File.AppendAllText(logPath,_logCacheStr);
		}
		lastStackFrameLength = _stackFrameLength;
	}
} 