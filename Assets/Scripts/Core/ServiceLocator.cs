using System;
using System.Collections.Generic;

namespace FrostbornRealms.Core {
    public static class ServiceLocator {
        private static readonly Dictionary<Type, object> _services = new();
        public static void Register<T>(T instance) where T: class { _services[typeof(T)] = instance; }
        public static T Get<T>() where T: class { return (T)_services[typeof(T)]; }
        public static bool TryGet<T>(out T value) where T: class {
            if (_services.TryGetValue(typeof(T), out var obj)) { value = (T)obj; return true; }
            value = null;
            return false;
        }
    }
}