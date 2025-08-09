// Minimal globals so sst.config.ts typechecks in CI
// NECESSARY BECAUSE OF THIS ISSUE: https://github.com/sst/sst/issues/5890
// REMOVE ASAP IF OR WHEN THAT IS RESOLVED. I DO NOT LIKE THIS. 
declare global {
  const $app: {
    stage: string;
    name: string;
    providers?: Record<string, any>;
  };

  function $config<T extends ConfigInput>(config: T): T;

  interface ConfigInput {
    app(input?: { stage?: string }): {
      name: string;
      removal?: "retain" | "remove";
      home?: "aws" | "cloudflare";
      providers?: {
        aws?: {
          region?: string;
          profile?: string;
        };
        cloudflare?: {
          accountId?: string;
        };
      };
    };
    run(): Promise<any> | any;
  }

  namespace sst {
    namespace aws {
      interface FunctionProps {
        handler: string;
        runtime?: string;
        architecture?: "x86_64" | "arm64";
        timeout?: string;
        memory?: string;
        url?: {
          cors?: {
            allowCredentials?: boolean;
            allowHeaders?: string[];
            allowMethods?: string[];
            allowOrigins?: string[];
            exposeHeaders?: string[];
            maxAge?: string;
          };
        };
        environment?: Record<string, string>;
        logging?: {
          retention?: string;
          format?: "text" | "json";
        };
        permissions?: Array<{
          actions: string[];
          resources: string[];
        }>;
      }

      class Function {
        constructor(name: string, props: FunctionProps);
        url: string;
        name: string;
        arn: string;
        nodes: {
          function: {
            name: string;
            arn: string;
          };
        };
      }

      // Add other commonly used SST components as needed
      class Bucket {
        constructor(name: string, props?: Record<string, any>);
        name: string;
        arn: string;
        url: string;
      }

      class Table {
        constructor(name: string, props?: Record<string, any>);
        name: string;
        arn: string;
      }
    }
  }
}

export {};