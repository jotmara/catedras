using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Mvc.ApplicationModels;
using Microsoft.IdentityModel.Tokens;
using System.Text;
using System.Text.Json;
using System.Threading.RateLimiting;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Repositorios;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

var builder = WebApplication.CreateBuilder(args);

// ── Dapper ────────────────────────────────────────────────────────────────────
// Mapear columnas snake_case (fk_asistente) a propiedades PascalCase (FkAsistente).
Dapper.DefaultTypeMap.MatchNamesWithUnderscores = true;

// Honrar [Column] en TODOS los modelos: sin esto, columnas como nombre_completo_asis
// o ventana_inicio (que es una proyeccion, no una columna real) no mapean.
foreach (var tipoModelo in typeof(ConexionHelper).Assembly.GetTypes()
             .Where(t => t.GetCustomAttributes(
                 typeof(System.ComponentModel.DataAnnotations.Schema.TableAttribute), false).Length > 0))
{
    Dapper.SqlMapper.SetTypeMap(tipoModelo, new Dapper.CustomPropertyTypeMap(tipoModelo, (tipo, columna) =>
        tipo.GetProperties().FirstOrDefault(p =>
            (p.GetCustomAttributes(
                typeof(System.ComponentModel.DataAnnotations.Schema.ColumnAttribute), false)
                .Cast<System.ComponentModel.DataAnnotations.Schema.ColumnAttribute>()
                .FirstOrDefault()?.Name ?? p.Name)
            .Equals(columna, StringComparison.OrdinalIgnoreCase)
            || p.Name.Equals(columna.Replace("_", ""), StringComparison.OrdinalIgnoreCase))!));
}

// Las columnas date llegan como DateTime; convertirlas a DateOnly.
Dapper.SqlMapper.AddTypeHandler(new DateOnlyTypeHandler());
Dapper.SqlMapper.AddTypeHandler(new DateOnlyNullableTypeHandler());
// Las columnas inet llegan como IPAddress; exponerlas como string.
Dapper.SqlMapper.AddTypeHandler(new InetTypeHandler());

// ── MVC ───────────────────────────────────────────────────────────────────────
builder.Services.AddControllers(o =>
{
    // No rechazar columnas string opcionales por el [Required] implicito.
    o.SuppressImplicitRequiredAttributeForNonNullableReferenceTypes = true;
    // Rutas [controller] en snake_case: /api/registro_asistencia.
    o.Conventions.Add(new RouteTokenTransformerConvention(new SnakeCaseRouteTransformer()));
    // Traduce las excepciones de PostgreSQL a codigos HTTP con sentido (RN-xx -> 422).
    o.Filters.Add<FiltroExcepcionPostgres>();
})
.AddJsonOptions(o =>
{
    // Exponer los campos con el nombre real de columna, igual que la base.
    o.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower;
});

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    // Entrega 1: Solo tablas independientes (sin claves foráneas)
    c.SwaggerDoc("entrega1", new Microsoft.OpenApi.Models.OpenApiInfo
    {
        Title = "ApiCatedrasUsbmed - Entrega 1 (Tablas Base sin FK)",
        Version = "entrega1",
        Description = "Primera Entrega: Entidades maestras independientes sin claves foráneas (Sede, Periodo, Tipos, Modalidad, Rol, Estado, Encuesta)."
    });

    // Versión Completa
    c.SwaggerDoc("v1", new Microsoft.OpenApi.Models.OpenApiInfo
    {
        Title = "ApiCatedrasUsbmed - Modelo Completo (37 Tablas Base + 6 Vistas)",
        Version = "v1",
        Description = "API Completa de Cátedras Abiertas - Universidad de San Buenaventura Medellín."
    });

    // Filtro por versión: en 'entrega1' solo se incluyen las 10 tablas sin FK + Autenticacion/Raiz
    c.DocInclusionPredicate((docName, apiDesc) =>
    {
        if (docName == "entrega1")
        {
            var controllerName = apiDesc.ActionDescriptor.RouteValues["controller"]?.ToLowerInvariant() ?? "";
            var tablasSinFk = new HashSet<string>
            {
                "sede",
                "periodoacademico",
                "tipodocumento",
                "tipovinculacion",
                "modalidad",
                "rol",
                "tipoevento",
                "tipopregunta",
                "estadoproceso",
                "encuesta",
                "autenticacion",
                "raiz"
            };
            return tablasSinFk.Contains(controllerName);
        }
        return true;
    });

    // Secciones por utilidad, no por alfabeto: Autenticacion primero.
    c.DocumentFilter<OrdenSwagger>();

    // Esquema Http+bearer, NO ApiKey: asi Swagger antepone la palabra "Bearer" el solo
    // y basta con pegar el JWT. Con ApiKey -que es como venia de ApiEvalFormativaUsbmed-
    // habia que escribir "Bearer " a mano, y olvidarlo daba un 401 desconcertante.
    c.AddSecurityDefinition("Bearer", new Microsoft.OpenApi.Models.OpenApiSecurityScheme
    {
        Description = "Pegue AQUI solamente el JWT que devuelve POST /api/autenticacion/token. "
                    + "No escriba la palabra Bearer: Swagger la antepone sola.",
        Name = "Authorization",
        In = Microsoft.OpenApi.Models.ParameterLocation.Header,
        Type = Microsoft.OpenApi.Models.SecuritySchemeType.Http,
        Scheme = "bearer",
        BearerFormat = "JWT"
    });
    c.AddSecurityRequirement(new Microsoft.OpenApi.Models.OpenApiSecurityRequirement
    {
        {
            new Microsoft.OpenApi.Models.OpenApiSecurityScheme
            {
                Reference = new Microsoft.OpenApi.Models.OpenApiReference
                { Type = Microsoft.OpenApi.Models.ReferenceType.SecurityScheme, Id = "Bearer" }
            },
            Array.Empty<string>()
        }
    });
});

// ── CORS ──────────────────────────────────────────────────────────────────────
// Sin origenes configurados no pasa ningun cross-origin. No se usa AllowAnyOrigin.
var origenesCors = builder.Configuration.GetSection("Cors:AllowedOrigins").Get<string[]>()
                   ?? Array.Empty<string>();
builder.Services.AddCors(o => o.AddPolicy("OrigenesPermitidos", p =>
{
    if (origenesCors.Length == 0) { p.WithOrigins("http://_sin_origenes_configurados_"); return; }
    p.WithOrigins(origenesCors).AllowAnyMethod().AllowAnyHeader();
}));

// ── Fail-fast de configuracion ────────────────────────────────────────────────
var jwtKey = builder.Configuration["Jwt:Key"];
if (string.IsNullOrWhiteSpace(jwtKey))
    throw new InvalidOperationException(
        "Jwt:Key no esta configurada. Defina la variable de entorno Jwt__Key o appsettings.");
if (jwtKey.Length < 32)
    throw new InvalidOperationException(
        "Jwt:Key es demasiado corta: HMAC-SHA256 necesita al menos 32 caracteres.");
if (string.IsNullOrWhiteSpace(builder.Configuration.GetConnectionString("Postgres")))
    throw new InvalidOperationException(
        "ConnectionStrings:Postgres no esta configurada.");

var jwtIssuer   = builder.Configuration["Jwt:Issuer"];
var jwtAudience = builder.Configuration["Jwt:Audience"];

builder.Services.AddAuthentication(o =>
{
    o.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    o.DefaultChallengeScheme    = JwtBearerDefaults.AuthenticationScheme;
})
.AddJwtBearer(o =>
{
    o.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuerSigningKey = true,
        IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtKey)),
        ValidateIssuer   = !string.IsNullOrWhiteSpace(jwtIssuer),
        ValidIssuer      = jwtIssuer,
        ValidateAudience = !string.IsNullOrWhiteSpace(jwtAudience),
        ValidAudience    = jwtAudience
    };
});
builder.Services.AddAuthorization();

// ── Limite de tasa del camino publico ─────────────────────────────────────────
// /api/acceso es anonimo y esta detras de un QR proyectado en un auditorio: sin limite
// seria un oraculo para enumerar el maestro de 14.808 personas y para fuerza bruta
// sobre la clave de 6 digitos.
builder.Services.AddRateLimiter(o =>
{
    o.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
    o.AddPolicy("acceso-publico", ctx =>
        RateLimitPartition.GetFixedWindowLimiter(
            partitionKey: ctx.Connection.RemoteIpAddress?.ToString() ?? "sin-ip",
            factory: _ => new FixedWindowRateLimiterOptions
            {
                PermitLimit = 10,
                Window = TimeSpan.FromMinutes(1),
                QueueLimit = 0
            }));
});

// ── Infraestructura ───────────────────────────────────────────────────────────
builder.Services.AddSingleton<IFabricaConexion, FabricaConexion>();
builder.Services.AddScoped<FiltroExcepcionPostgres>();

// ── Repositorios y servicios por tabla y por vista (generados) ────────────────
builder.Services.AddScoped<IAliasProgramaRepositorio, AliasProgramaRepositorio>();
builder.Services.AddScoped<IAliasProgramaServicio,    AliasProgramaServicio>();
builder.Services.AddScoped<IAsistenteRepositorio, AsistenteRepositorio>();
builder.Services.AddScoped<IAsistenteServicio,    AsistenteServicio>();
builder.Services.AddScoped<IBitacoraRepositorio, BitacoraRepositorio>();
builder.Services.AddScoped<IBitacoraServicio,    BitacoraServicio>();
builder.Services.AddScoped<ICatedraRepositorio, CatedraRepositorio>();
builder.Services.AddScoped<ICatedraServicio,    CatedraServicio>();
builder.Services.AddScoped<IClaveAccesoRepositorio, ClaveAccesoRepositorio>();
builder.Services.AddScoped<IClaveAccesoServicio,    ClaveAccesoServicio>();
builder.Services.AddScoped<IConsentimientoDatosRepositorio, ConsentimientoDatosRepositorio>();
builder.Services.AddScoped<IConsentimientoDatosServicio,    ConsentimientoDatosServicio>();
builder.Services.AddScoped<IDependenciaRepositorio, DependenciaRepositorio>();
builder.Services.AddScoped<IDependenciaServicio,    DependenciaServicio>();
builder.Services.AddScoped<IDetalleMigracionRepositorio, DetalleMigracionRepositorio>();
builder.Services.AddScoped<IDetalleMigracionServicio,    DetalleMigracionServicio>();
builder.Services.AddScoped<IDocumentoAsistenteRepositorio, DocumentoAsistenteRepositorio>();
builder.Services.AddScoped<IDocumentoAsistenteServicio,    DocumentoAsistenteServicio>();
builder.Services.AddScoped<IEncuestaRepositorio, EncuestaRepositorio>();
builder.Services.AddScoped<IEncuestaServicio,    EncuestaServicio>();
builder.Services.AddScoped<IEnlaceRegistroRepositorio, EnlaceRegistroRepositorio>();
builder.Services.AddScoped<IEnlaceRegistroServicio,    EnlaceRegistroServicio>();
builder.Services.AddScoped<IEstadoProcesoRepositorio, EstadoProcesoRepositorio>();
builder.Services.AddScoped<IEstadoProcesoServicio,    EstadoProcesoServicio>();
builder.Services.AddScoped<IFacultadRepositorio, FacultadRepositorio>();
builder.Services.AddScoped<IFacultadServicio,    FacultadServicio>();
builder.Services.AddScoped<ILoteCargaAsistenteRepositorio, LoteCargaAsistenteRepositorio>();
builder.Services.AddScoped<ILoteCargaAsistenteServicio,    LoteCargaAsistenteServicio>();
builder.Services.AddScoped<ILoteMigracionRepositorio, LoteMigracionRepositorio>();
builder.Services.AddScoped<ILoteMigracionServicio,    LoteMigracionServicio>();
builder.Services.AddScoped<IModalidadRepositorio, ModalidadRepositorio>();
builder.Services.AddScoped<IModalidadServicio,    ModalidadServicio>();
builder.Services.AddScoped<INovedadCargaRepositorio, NovedadCargaRepositorio>();
builder.Services.AddScoped<INovedadCargaServicio,    NovedadCargaServicio>();
builder.Services.AddScoped<IOpcionPreguntaRepositorio, OpcionPreguntaRepositorio>();
builder.Services.AddScoped<IOpcionPreguntaServicio,    OpcionPreguntaServicio>();
builder.Services.AddScoped<IParametroRepositorio, ParametroRepositorio>();
builder.Services.AddScoped<IParametroServicio,    ParametroServicio>();
builder.Services.AddScoped<IPeriodoAcademicoRepositorio, PeriodoAcademicoRepositorio>();
builder.Services.AddScoped<IPeriodoAcademicoServicio,    PeriodoAcademicoServicio>();
builder.Services.AddScoped<IPonenciaRepositorio, PonenciaRepositorio>();
builder.Services.AddScoped<IPonenciaServicio,    PonenciaServicio>();
builder.Services.AddScoped<IPreguntaRepositorio, PreguntaRepositorio>();
builder.Services.AddScoped<IPreguntaServicio,    PreguntaServicio>();
builder.Services.AddScoped<IProgramaAcademicoRepositorio, ProgramaAcademicoRepositorio>();
builder.Services.AddScoped<IProgramaAcademicoServicio,    ProgramaAcademicoServicio>();
builder.Services.AddScoped<IProgramaAsistenteRepositorio, ProgramaAsistenteRepositorio>();
builder.Services.AddScoped<IProgramaAsistenteServicio,    ProgramaAsistenteServicio>();
builder.Services.AddScoped<IRegistroAsistenciaRepositorio, RegistroAsistenciaRepositorio>();
builder.Services.AddScoped<IRegistroAsistenciaServicio,    RegistroAsistenciaServicio>();
builder.Services.AddScoped<IRespuestaEncuestaRepositorio, RespuestaEncuestaRepositorio>();
builder.Services.AddScoped<IRespuestaEncuestaServicio,    RespuestaEncuestaServicio>();
builder.Services.AddScoped<IRespuestaItemRepositorio, RespuestaItemRepositorio>();
builder.Services.AddScoped<IRespuestaItemServicio,    RespuestaItemServicio>();
builder.Services.AddScoped<IRolRepositorio, RolRepositorio>();
builder.Services.AddScoped<IRolServicio,    RolServicio>();
builder.Services.AddScoped<IRolPorUsuarioRepositorio, RolPorUsuarioRepositorio>();
builder.Services.AddScoped<IRolPorUsuarioServicio,    RolPorUsuarioServicio>();
builder.Services.AddScoped<ISedeRepositorio, SedeRepositorio>();
builder.Services.AddScoped<ISedeServicio,    SedeServicio>();
builder.Services.AddScoped<ISesionRepositorio, SesionRepositorio>();
builder.Services.AddScoped<ISesionServicio,    SesionServicio>();
builder.Services.AddScoped<ITipoDocumentoRepositorio, TipoDocumentoRepositorio>();
builder.Services.AddScoped<ITipoDocumentoServicio,    TipoDocumentoServicio>();
builder.Services.AddScoped<ITipoEventoRepositorio, TipoEventoRepositorio>();
builder.Services.AddScoped<ITipoEventoServicio,    TipoEventoServicio>();
builder.Services.AddScoped<ITipoPreguntaRepositorio, TipoPreguntaRepositorio>();
builder.Services.AddScoped<ITipoPreguntaServicio,    TipoPreguntaServicio>();
builder.Services.AddScoped<ITipoVinculacionRepositorio, TipoVinculacionRepositorio>();
builder.Services.AddScoped<ITipoVinculacionServicio,    TipoVinculacionServicio>();
builder.Services.AddScoped<IUsuarioRepositorio, UsuarioRepositorio>();
builder.Services.AddScoped<IUsuarioServicio,    UsuarioServicio>();
builder.Services.AddScoped<IVAsistenciaCompletaRepositorio, VAsistenciaCompletaRepositorio>();
builder.Services.AddScoped<IVAsistenciaCompletaServicio,    VAsistenciaCompletaServicio>();
builder.Services.AddScoped<IVAsistenteVigenteRepositorio, VAsistenteVigenteRepositorio>();
builder.Services.AddScoped<IVAsistenteVigenteServicio,    VAsistenteVigenteServicio>();
builder.Services.AddScoped<IVControlVentanaRepositorio, VControlVentanaRepositorio>();
builder.Services.AddScoped<IVControlVentanaServicio,    VControlVentanaServicio>();
builder.Services.AddScoped<IVEmbudoRegistroRepositorio, VEmbudoRegistroRepositorio>();
builder.Services.AddScoped<IVEmbudoRegistroServicio,    VEmbudoRegistroServicio>();
builder.Services.AddScoped<IVEvaluacionSesionRepositorio, VEvaluacionSesionRepositorio>();
builder.Services.AddScoped<IVEvaluacionSesionServicio,    VEvaluacionSesionServicio>();
builder.Services.AddScoped<IVPendienteMigracionRepositorio, VPendienteMigracionRepositorio>();
builder.Services.AddScoped<IVPendienteMigracionServicio,    VPendienteMigracionServicio>();
builder.Services.AddScoped<IVinculacionAsistenteRepositorio, VinculacionAsistenteRepositorio>();
builder.Services.AddScoped<IVinculacionAsistenteServicio,    VinculacionAsistenteServicio>();

// ── Autenticacion de administrador (camino A) ────────────────────────────────
builder.Services.AddScoped<IAutenticacionRepositorio, AutenticacionRepositorio>();
builder.Services.AddScoped<IAutenticacionServicio,    AutenticacionServicio>();

// ── Metadata de tablas (information_schema) ──────────────────────────────────
builder.Services.AddScoped<IEstructuraRepositorio, EstructuraRepositorio>();
builder.Services.AddScoped<IEstructuraServicio,    EstructuraServicio>();

// ── Capa de PROCESOS ─────────────────────────────────────────────────────────
// No existe en ApiEvalFormativaUsbmed. Aqui el registro de un asistente no es un INSERT:
// es pedir clave, validarla y registrar con instantaneas, dentro de la ventana y
// respetando el cupo. Esos repositorios LLAMAN A LAS RUTINAS de la base.
builder.Services.AddScoped<IProcesoAccesoRepositorio, ProcesoAccesoRepositorio>();
builder.Services.AddScoped<IProcesoAccesoServicio,    ProcesoAccesoServicio>();
builder.Services.AddScoped<IProcesoEnlaceRepositorio, ProcesoEnlaceRepositorio>();
builder.Services.AddScoped<IProcesoEnlaceServicio,    ProcesoEnlaceServicio>();
builder.Services.AddScoped<IProcesoMigracionRepositorio, ProcesoMigracionRepositorio>();
builder.Services.AddScoped<IProcesoMigracionServicio,    ProcesoMigracionServicio>();

// ── Correo: apagado salvo Correo:Activo=true (config-gated, fail-closed) ─────
builder.Services.AddScoped<IServicioCorreo, ServicioCorreo>();

var app = builder.Build();

// Aviso de arranque: si no hay cadena del rol minimo, se usa la administrativa.
if (string.IsNullOrWhiteSpace(builder.Configuration.GetConnectionString("PostgresApp")))
    app.Logger.LogWarning(
        "ConnectionStrings:PostgresApp no esta configurada: el camino publico usara la " +
        "conexion administrativa. En produccion debe usar el rol rol_app_registro.");

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/entrega1/swagger.json", "Entrega 1 - Tablas Base (Sin Claves Foraneas)");
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "Modelo Completo (37 Tablas Base + 6 Vistas)");
        c.RoutePrefix = "swagger";
    });
}
app.UseCors("OrigenesPermitidos");
app.UseRateLimiter();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
app.Run();
