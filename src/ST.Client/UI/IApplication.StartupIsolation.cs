namespace System.Application.UI
{
    partial interface IApplication
    {
        static bool GetStartupIsolationFlag(string environmentVariableName)
        {
            var value = Environment.GetEnvironmentVariable(environmentVariableName);
            if (string.IsNullOrWhiteSpace(value))
            {
                return false;
            }

            return value.Equals("1", StringComparison.OrdinalIgnoreCase) ||
                   value.Equals("true", StringComparison.OrdinalIgnoreCase) ||
                   value.Equals("yes", StringComparison.OrdinalIgnoreCase) ||
                   value.Equals("on", StringComparison.OrdinalIgnoreCase);
        }

        public static bool SkipAppCenterInit => GetStartupIsolationFlag("STEAMPP_SKIP_APPCENTER");

        public static bool SkipNotifyIconInit => GetStartupIsolationFlag("STEAMPP_SKIP_NOTIFYICON");

        public static bool SkipWebView2Init => GetStartupIsolationFlag("STEAMPP_SKIP_WEBVIEW2_INIT");

        public static bool SkipStartupBackground => GetStartupIsolationFlag("STEAMPP_SKIP_STARTUP_BACKGROUND");

        public static bool SkipReverseProxyStartup => GetStartupIsolationFlag("STEAMPP_SKIP_REVERSE_PROXY_STARTUP");
    }
}
